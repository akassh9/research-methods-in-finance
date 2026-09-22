version 19.0
* Start with the repository root as your Stata working directory.
cd "week-03"
capture noisily do "assignment2.do"
local rc = _rc
cd ".."
if `rc' != 0 exit `rc'
