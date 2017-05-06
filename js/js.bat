REM Helper script for development on windows
call npm install
call jupyter nbextension install --py --sys-prefix exawidgets
call jupyter nbextension enable --py --sys-prefix exawidgets
