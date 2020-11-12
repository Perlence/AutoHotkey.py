#NoEnv
#Warn, All, MsgBox
SendMode, Input
SetBatchLines, -1

freq := ""
start := ""
end := ""
best := 999999999999999999999999999999
worst = 0
loops := 5000
DllCall("QueryPerformanceFrequency", "Int64*", freq)
Loop, 20 {
    DllCall("QueryPerformanceCounter", "Int64*", start)
    Loop, % loops {
        EnvGet, x, TEMP
    }
    DllCall("QueryPerformanceCounter", "Int64*", end)
    dur := (end - start) / freq / loops * 1000000
    if (dur < best) {
        best := dur
    }
    if (worst < dur) {
        worst := dur
    }
}
MsgBox, % best " " worst
; 0.11 - 0.16 usec per loop
