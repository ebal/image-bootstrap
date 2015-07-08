# Copyright (C) 2015 Sebastian Pipping <sebastian@pipping.org>
# Licensed under AGPL v3 or later

import directory_bootstrap.shared.loaders._argparse as argparse

from directory_bootstrap.distros.arch import ArchBootstrapper
from directory_bootstrap.distros.base import BOOTSTRAPPER_CLASS_FIELD, \
        add_general_directory_bootstrapping_options
from directory_bootstrap.distros.gentoo import GentooBootstrapper
from directory_bootstrap.shared.executor import Executor
from directory_bootstrap.shared.messenger import Messenger, \
        VERBOSITY_VERBOSE
from directory_bootstrap.shared.metadata import VERSION_STR
from directory_bootstrap.shared.output_control import \
        add_output_control_options, is_color_wanted, run_handle_errors


def _main__level_three(messenger, options):
    stdout_wanted = options.verbosity is VERBOSITY_VERBOSE

    if stdout_wanted:
        child_process_stdout = None
    else:
        child_process_stdout = open('/dev/null', 'w')

    executor = Executor(messenger, stdout=child_process_stdout)


    bootstrapper_class = getattr(options, BOOTSTRAPPER_CLASS_FIELD)
    bootstrap = bootstrapper_class.create(messenger, executor, options)

    bootstrap.check_for_commands()
    if bootstrap.wants_to_be_unshared():
        bootstrap.unshare()
    bootstrap.run()


    if not stdout_wanted:
        child_process_stdout.close()


def _main__level_two():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=VERSION_STR)

    add_output_control_options(parser)

    general = parser.add_argument_group('general configuration')
    add_general_directory_bootstrapping_options(general)

    system = parser.add_argument_group('system configuration')
    system.add_argument('--resolv-conf', metavar='FILE', default='/etc/resolv.conf',
        help='file to copy nameserver entries from (default: %(default)s)')

    distros = parser.add_subparsers(title='subcommands (choice of distribution)',
            description='Run "%(prog)s DISTRIBUTION --help" for details '
                    'on options specific to that distribution.',
            metavar='DISTRIBUTION', help='choice of distribution, pick from:')


    for strategy_clazz in (
            ArchBootstrapper,
            GentooBootstrapper,
            ):
        strategy_clazz.add_parser_to(distros)


    parser.add_argument('target_dir', metavar='DIRECTORY')

    options = parser.parse_args()


    messenger = Messenger(options.verbosity, is_color_wanted(options))
    run_handle_errors(_main__level_three, messenger, options)


def main():
    try:
        _main__level_two()
    except KeyboardInterrupt:
        pass
