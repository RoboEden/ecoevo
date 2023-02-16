# Change log

## version 0.1.7.dev3
- MOD ignore item amount in map file, use config instead
- ADD 8 item dense map
- ADD xlsx map generate script

## version 0.1.7.dev2
- MOD critical logging level to warning level
- ADD tool.pytest.ini_options
- ADD lambda panel generate script

## version 0.1.7.dev1
- FIX error in unit test

## version 0.1.6
  - ADD wipeout action
  - FIX item utility not passed to analyser
  - ADD render_mode
  - DEPRECATE `num_player`
  - UPDATE README.md
  - ADD item utility and related stastics
  - MOD analyser key generate
  - ADD utility plot script
  - FIX trade line trade amount display bug
  - FIX "Last Action" display. Now show proposed action.
  - ADD persona collect match ratio info
  - ADD price info and item exchange cnt info
  - FIX refresh item should be executed before obs generation

## version 0.1.5
- render:
  - ADD last_action and info
  - FIX trade_line still exists after reset
  - FIX trade_line displays incompletely
- env:
  - ADD random generate map on env reset
  - ADD Beldon's utility
  - MOD improve test framework
  - MOD parameters: bag volume 1e8; trade radius 7
  - MOD log utility coefficients: disposable 3; luxury 3
  - MOD add more test case
  - FIX health decrease bug
  - FIX item refresh time bug
  - FIX analyser trade times
  - FIX total step results to be 1 more than expected
  - FIX analyser info current step

## version 0.1.4
- ADD transaction_graph in env step info
- FIX test helper bug

## version 0.1.3
- ADD WebApp for render
- ADD control panel for WebApp

## version 0.1.2
- Add sanity check for `Player`
- Fix bug when render sell offer