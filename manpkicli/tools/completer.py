import readline
import builtins
from . import Command
from ..logger import log


class BufferAwareCompleter:
    _options = {}
    _current_candidates = []

    @staticmethod
    def reset_complete():
        BufferAwareCompleter._options = {}

    @staticmethod
    def _build_default():
        options = {}
        for dft in ["info", "help", "history", "connect", "disconnect", "exit", "end", "show", "debug"]:
            options[dft] = []
        return options

    @staticmethod
    def build_complete():
        cmds = Command.get_commands_context(builtins.current_context)
        log.debug(cmds)
        BufferAwareCompleter._options = BufferAwareCompleter._build_default()
        for cmd in cmds:
            log.debug(cmd)
            if cmd:
                token_split = cmd.get_command().split(' ')
                if ' '.join(token_split[:-1]) not in BufferAwareCompleter._options.keys():
                    BufferAwareCompleter._options[' '.join(token_split[:-1])] = []
                if len(token_split) > 1 and token_split[-1] not in BufferAwareCompleter._options[' '.join(token_split[:-1])]:
                    BufferAwareCompleter._options[' '.join(token_split[:-1])].append(token_split[-1])
        for ctxt in Command.get_all_context():
            if ctxt and ctxt not in BufferAwareCompleter._options.keys():
                BufferAwareCompleter._options[ctxt] = []
        log.debug("build_complete")

    @staticmethod
    def complete(text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            BufferAwareCompleter.build_complete()
            log.debug(BufferAwareCompleter._options)

            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()
            if not words:
                BufferAwareCompleter._current_candidates = sorted(BufferAwareCompleter._options.keys())
            else:
                try:
                    if begin == 0:
                        # first word
                        candidates = BufferAwareCompleter._options.keys()
                    else:
                        # later word
                        first = ' '.join(words[:repr(origline).count(' ')])
                        max_space = repr(origline).count(' ')
                        i = 1
                        while first not in BufferAwareCompleter._options.keys() and i < max_space:
                            first = ' '.join(words[:repr(origline).count(' ')-i])
                            i += 1
                        log.debug('here')
                        log.debug(first)
                        candidates = BufferAwareCompleter._options[first]
                    log.debug('being_complete : %s', being_completed)
                    if being_completed:
                        # match options with portion of input
                        # being completed
                        BufferAwareCompleter._current_candidates = [w for w in candidates
                                                   if w and w.startswith(being_completed)]
                        log.debug(BufferAwareCompleter._current_candidates)
                        if '[param]' in BufferAwareCompleter._current_candidates or \
                                '[param=value]' in BufferAwareCompleter._current_candidates:
                            log.debug('here')
                            cmds = Command.search_completer_command(origline, builtins.current_context)
                            log.debug(cmds)

                    else:
                        # matching empty string so use all candidates
                        BufferAwareCompleter._current_candidates = candidates
                        if '[param]' in BufferAwareCompleter._current_candidates or \
                                '[param=value]' in BufferAwareCompleter._current_candidates:
                            log.debug('here')
                            cmds = Command.search_completer_command(origline, builtins.current_context)
                            log.debug(cmds)
                            candidates = []
                            param_mandatory_completed = True
                            log.debug(cmds.get_params())
                            for param in cmds.get_params():
                                log.debug(param['name'])
                                if param['name'] not in candidates:
                                    candidates.append(param['name'])
                                if param['mandatory'] and param['name']+'=' not in origline:
                                    param_mandatory_completed = False
                            if param_mandatory_completed:
                                candidates.append('<CR>')
                            BufferAwareCompleter._current_candidates = candidates

                except (KeyError, IndexError) as err:
                    log.error('completion error: %s', err)
                    BufferAwareCompleter._current_candidates = []

        try:
            response = BufferAwareCompleter._current_candidates[state]
        except IndexError:
            response = None
        log.debug('complete(%s, %s) => %s', repr(text), state, response)
        return response
