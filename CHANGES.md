# Change log

## version 0.2.1
- MOD render to use redux
- ADD bag volume limit in ui
- FIX bag volume display in ui
- FIX ui show debug log
- MOD adjust ui layout

## version 0.2.0
- ADD offer accept mechanism
- MOD rewrite player action execution
- FIX render trade line
- ADD more test

## version 0.1.8
- ADD new webapp support stream play game scene

## version 0.1.7
- ADD move solver
- MOD parameters generation logic for items and players, from yaml to py
- MOD consume num for disposable and divisible items
- MOD ignore item amount in map file, use config instead
- ADD 8 item dense map
- MOD critical logging level to warning level
- ADD tool.pytest.ini_options
- ADD xlsx map generate script
- ADD lambda panel generate script
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
