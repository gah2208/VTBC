________________________________________
✅ ✅  HANDOFF DOCUMENT

PHASE 1
________________________________________
✅ SYSTEM NAME
Vertical to Butterfly Conversion (VTBC)
Version: 1.0.0 (LOCKED)
✅ ✅ CARDINAL DEVELOPMENT RULES (CDR = reminder to copilot to apply all of the following rules)
 	Never rewrite existing files without written permission from Greg
 	Always edit files surgically.
 	Always send the full updated files after a change is made. 
 	Limit explanations to what was broken, what was fixed, and the full code for the entire file.
 	When changes are made, update the version number. 1.2.3
 3 is bug fixes done surgically
 2 is addition of new functionality done surgically
 1 is major authorized rewrite. 
________________________________________
✅ ✅ SYSTEM STATUS
✅ Architecturally complete
✅ Execution-correct
✅ No structural defects
✅ No placeholders
✅ No proxy data
✅ Fully synchronized codebase
________________________________________
✅ ✅ SYSTEM PURPOSE
Automated SPX options trading system that:
•	Detects directional trend via EMA alignment
•	Filters trades using directional expected move
•	Executes butterflies via sequential vertical spreads
•	Holds all positions through expiration
________________________________________
✅ ✅ END-TO-END FLOW
SPX → ATM → EMA → Signal → EM filter → K selection → Entry → Fill → Conversion → Butterfly → Expiration
________________________________________
✅ ✅ DATA MODEL
✅ SPX (Primary Input)
•	Pulled continuously from TradeStation API
•	Used for: 
o	EMA calculation ✅
o	strike selection ✅
________________________________________
✅ ATM
ATM = round(SPX / STRIKE_STEP) * STRIKE_STEP
Used for:
•	EM calculation
•	option lookup
________________________________________
✅ EMA INPUT (FINAL)
EMA input = SPX price
✅ No proxy
✅ No distortion
✅ Fully aligned with underlying
________________________________________
✅ ✅ EMA SYSTEM 
Label	Period	Function
EMA3	260	Fast
EMA5	475	Medium
EMA20	1885	Slow
________________________________________
✅ Update Loop
•	Every ~2 seconds
________________________________________
✅ Rebuild (Startup Only)
EMA	Data
EMA20	120 minutes
EMA5	last 15 minutes
EMA3	last 9 minutes
________________________________________
✅ ✅ TREND LOGIC
✅ UP
EMA3 > EMA5 > EMA20
AND EMA3 rising
________________________________________
✅ DOWN
EMA3 < EMA5 < EMA20
AND EMA3 falling
________________________________________
✅ Otherwise
NO TRADE
________________________________________
✅ ✅ EXPECTED MOVE (EM)
✅ Definition
Direction	EM
CALL	ATM call mid
PUT	ATM put mid
________________________________________
✅ Entry Condition
EM ≥ MIN_EM
________________________________________
✅ ✅ PRICE FILTER
option_mid ≤ MAX_PREMIUM
________________________________________
✅ ✅ STRIKE MODEL
✅ Separation of Roles
Purpose	Variable
Market reference	ATM
Trade execution	K
________________________________________
✅ K Selection
CALL (UP trend)
K = smallest strike ≥ SPX
PUT (DOWN trend)
K = largest strike ≤ SPX
________________________________________
✅ Guaranteed behavior
SPX	CALL K	PUT K
7002	7005	7000
7004.99	7005	7000
7000.01	7005	7000
________________________________________
✅ ✅ TRADE CONSTRUCTION
________________________________________
✅ ENTRY (Vertical)
CALL
BUY  K
SELL K + W
PUT
BUY  K
SELL K - W
________________________________________
✅ CONVERSION (Vertical)
Triggered when long position fills
CALL
SELL K + W
BUY  K + 2W
PUT
SELL K - W
BUY  K - 2W
________________________________________
✅ RESULTING STRUCTURE
CALL Butterfly
K / K+W / K+2W
PUT Butterfly
K / K-W / K-2W
________________________________________
✅ ✅ CONVERSION PRICING (FINAL)
conversion_price = entry_price × PROFIT_MULTIPLIER
Default:
PROFIT_MULTIPLIER = 1.2
________________________________________
✅ Interpretation
•	Minimum expected profit: +20%
•	Directly tied to trade cost
•	No arbitrary pricing
________________________________________
✅ ✅ STATE MACHINE
IDLE
→ LONG_WORKING
→ CONVERSION_WORKING
→ IDLE
________________________________________
✅ Key rule
✅ Conversion uses stored entry direction (state.direction)
❌ NOT current market trend
________________________________________
✅ ✅ STRIKE SAFETY SYSTEM
✅ CALL
block if:
K in call_short_strikes
(K+W) in call_long_strikes
________________________________________
✅ PUT
block if:
K in put_short_strikes
(K-W) in put_long_strikes
________________________________________
✅ Prevents
•	overlapping butterflies
•	inverted structures
•	strike conflicts
________________________________________
✅ ✅ POSITION MODEL
________________________________________
✅ Normal Intraday Flow
long → conversion → butterfly
→ Fully hedged
→ $0 risk structure
________________________________________
✅ End-of-day forced conversion
•	used for incomplete trades
•	reduces loss vs closing long
•	preserves potential payoff
________________________________________
✅ Lifetime
Positions held until expiration
NO exits
________________________________________
✅ ✅ ORDER MODEL
•	Multi-leg vertical spreads
•	Single submission per structure
•	Limit orders
•	GTC duration
________________________________________
✅ ✅ API SYSTEM
•	OAuth refresh token flow
•	Access token auto-refresh
•	Retry logic
•	Failure threshold protection
________________________________________
✅ ✅ FILE INVENTORY (FINAL)
File	Purpose	Version
config.py	parameters	1.0.0
main.py	orchestration	1.0.0
ema_engine.py	EMA math	1.0.0
ema_rebuild.py	EMA initialization	1.0.0
eligibility_engine.py	signal logic	1.0.0
execution_state.py	state machine	1.0.0
market_data.py	data + rebuild input	1.0.0
order_builder.py	symbol formatting	1.0.0
ts_client.py	API client	1.0.0
ema_persistence.py	EMA persistence	1.0.0
________________________________________
✅ ✅ KNOWN LIMITATIONS (INTENTIONAL)
•	No partial fill handling
•	No intraday position closing
•	No dynamic pricing refinement
👉 All are explicit design decisions, not defects
________________________________________
✅ ✅ FINAL SYSTEM CLASSIFICATION
Category	Status
Architecture	✅ Complete
Trading Logic	✅ Correct
Execution Logic	✅ Correct
Risk Model	✅ Consistent
Data Integrity	✅ Correct
Remaining Unknowns	❌ None
________________________________________
✅ ✅ ONE-LINE SYSTEM DEFINITION
A fully automated SPX options trading engine that uses EMA-based trend detection and directional expected move filtering to construct butterflies via sequential vertical spreads, with deterministic risk containment and expiration-based payoff realization.
________________________________________
✅ ✅ FINAL STATUS
✅ SYSTEM LOCKED — HANDOFF READY
________________________________________
✅ ✅ One-line closing
✅ Tomorrow is strictly about verifying API connectivity and observing real order flow — not debugging logic.
________________________________________
 
PHASE 2
✅ ✅ ADDENDUM — POST HANDOFF CHANGES
DATE: 2026-05-28
VERSION: 1.2.1
------------------------------------------------------------

✅ AUTH SYSTEM (NEW)
- GitHub auth.json controls access
- Fail-closed: no auth = exit
- Machine ID enforced
- Unauthorized → admin alert

✅ VERSION CONTROL (NEW)
- __version__ vs auth.json min_version
- Soft update prompt
- No forced updates

✅ UPDATE SYSTEM (NEW)
- Update.bat integration
- User-triggered updates

✅ CONFIG EDITOR CHANGES
- POSITIONS dual-mode (contracts or % capital)
- Real-time validation + UI hint
- Buttons centered and evenly spaced
- Credentials protected on restore

✅ UI FIXES
- Removed fullscreen zoom behavior
- Geometry locked BEFORE UI build
- Startup sequence stabilized
- Flicker and resize removed

✅ BUILD SYSTEM
- python -m PyInstaller --noconsole --onefile config_editor.py

✅ PROCESS HANDLING
- EXE may persist after close
- Use taskkill if needed

✅ VERSION POLICY
- 1.2.1 current
- Patch = bug fix
- Minor = feature
- Major = rewrite

✅ FINAL SYSTEM STATE
- Centrally controlled
- Fail-secure
- Version governed
- UI stable
- Production ready

✅ FINAL INSTRUCTION
- CDR enforcement mandatory
- No rewrites
- No structural collapse
- Only surgical edits

 
________________________________________
✅ ✅ VTBC CARDINAL DEVELOPMENT RULES (CDR) ENFORCEMENT CHECKLIST

________________________________________
✅ ✅ 🔒 PRE-CHANGE CHECK (MUST PASS BEFORE WRITING CODE)
✅ 1. Scope Control
•	Is the task explicitly requested?
•	Is the change limited to a specific behavior or bug?
•	Am I avoiding “while I’m here” improvements?
________________________________________
✅ 2. File Boundary
•	Am I modifying only the required file(s)?
•	Am I NOT creating new files unless explicitly instructed?
•	Am I avoiding touching unrelated modules?
________________________________________
✅ 3. Architecture Protection
•	Am I preserving: 
o	execution flow
o	state machine
o	module boundaries
•	No redesign or refactor introduced?
________________________________________
________________________________________
✅ ✅ ⚙️ CHANGE EXECUTION CHECK
✅ 4. Surgical Edit Only
•	Is the change minimal?
•	Are all other lines untouched?
•	No reformatting beyond the change?
________________________________________
✅ 5. No Structural Drift
•	No sections removed?
•	No ordering changed?
•	No collapsing or condensing code?
________________________________________
✅ 6. No Assumptions
•	Using only provided logic?
•	No inferred functionality added?
•	No “guessing what should exist”?
________________________________________
________________________________________
✅ ✅ 📦 POST-CHANGE VALIDATION CHECK
✅ 7. Full File Compliance
•	Entire file returned ✅
•	File is drop in ready ✅
•	No missing imports / dependencies ✅
________________________________________
✅ 8. Version Update
•	__version__ incremented correctly?
•	Correct type: 
o	Patch (bug fix)
o	Minor (feature)
o	Major (rewrite, authorized only)
________________________________________
✅ 9. System Integrity
•	Does NOT break: 
o	build_check
o	checksum validation
o	Update.bat
o	Restore.bat
o	VERSION.txt logic
________________________________________
 
✅ 10. Behavioral Safety
•	Does this change affect anything outside requested scope? 
o	If YES → ❌ STOP
________________________________________
________________________________________
✅ ✅ 🚨 FAIL CONDITIONS (AUTO-REJECT)
If ANY of these occur → REJECT CHANGE
•	❌ File rewritten instead of edited
•	❌ Code shortened or simplified
•	❌ Sections removed or reorganized
•	❌ Version not updated
•	❌ Multiple files changed unnecessarily
•	❌ Logic altered outside scope
•	❌ Any assumption introduced
________________________________________
________________________________________
✅ ✅ 🧠 FINAL DECISION RULE
Before submitting, ask:
"Did I ONLY change what was explicitly requested?"
•	If YES → ✅ proceed
•	If NO → ❌ revert
________________________________________
________________________________________
✅ ✅ ✅ ONE-LINE EXECUTION RULE
Modify only what is required. Preserve everything else exactly.
________________________________________
________________________________________
 
PHASE 3
✅ VTBC Build Handoff Document (FLAT MODE)
6/05/2026
________________________________________
📦 SYSTEM OVERVIEW
This build system compiles Python scripts into standalone .exe files using PyInstaller, with a flat directory structure to eliminate path ambiguity.
________________________________________
📁 REQUIRED DIRECTORY STRUCTURE
All files must exist directly in:
C:\VTBC\
✅ Required files
C:\VTBC\
│
├── main.py
├── config_editor.py
├── restore_defaults.py
│
├── config_default.json
├── config.json   (optional at first run)
│
├── Build1_Dev.ps1
├── Build1_Dev.bat
________________________________________
🔧 BUILD PROCESS
✅ Run build
Build1_Dev.bat
What it does:
•	Forces working directory → C:\VTBC
•	Deletes: 
o	build\
o	all .spec
•	Runs PyInstaller for: 
o	main.py
o	config_editor.py
o	restore_defaults.py
•	Outputs .exe files directly into: 
•	C:\VTBC\
________________________________________
📤 BUILD OUTPUT
After build:
C:\VTBC\
│
├── main.exe
├── config_editor.exe
├── restore_defaults.exe
________________________________________
⚙️ RUNTIME BEHAVIOR
✅ config_editor.exe
•	Reads: 
•	C:\VTBC\config_default.json
•	Loads configuration at startup
________________________________________
✅ restore_defaults.exe
•	Reads: 
•	C:\VTBC\config_default.json
•	Writes: 
•	C:\VTBC\config.json
________________________________________
⚠️ CRITICAL RULES
✅ MUST FOLLOW
•	All paths are flat (root only)
•	No subfolders like: 
o	❌ dev
o	❌ src
o	❌ config\
________________________________________
✅ Python path standard (EXE-safe)
All scripts must use:
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(file)
Then:
os.path.join(BASE_DIR, "filename")
________________________________________
❌ DO NOT USE
•	Relative paths (../)
•	Hardcoded dev paths (dev\config)
•	Subdirectories (config\...)
________________________________________
🔍 TROUBLESHOOTING
EXE flashes and closes
Run:
cd C:\VTBC
config_editor.exe
✅ Shows actual error
________________________________________
Common failure
❌ File not found:
config_default.json
✅ Fix:
Ensure file exists:
C:\VTBC\config_default.json
________________________________________
Spec/build showing in wrong folder
✅ Cause:
Wrong working directory
✅ Fix:
Always run via:
Build1_Dev.bat
________________________________________
🔒 VERSION CONTROL REQUIREMENT
Every change MUST include:
Requirement	Status
Surgical modification	✅
Version updated	✅
VERSION.txt updated	✅
CHANGELOG.txt updated	✅
👉 If ANY item = ❌ → STOP
________________________________________
🧠 DESIGN DECISION
Flat architecture chosen to eliminate:
•	working directory issues ✅
•	PyInstaller path inconsistencies ✅
•	dev vs runtime mismatch ✅
•	missing file errors ✅
________________________________________
✅ FINAL STATE
System is now:
•	Deterministic ✅
•	Flat ✅
•	Path-safe ✅
•	EXE-stable ✅
________________________________________
If you want next step: ✅ integrate validate script before build
✅ or lock Build_ALL to enforce flat invariants automatically


