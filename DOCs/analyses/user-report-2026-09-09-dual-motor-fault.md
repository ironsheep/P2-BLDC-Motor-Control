# User report — 2026-09-09 — dual-motor demo faults on repeat runs

Received by email. Reproduced verbatim below; analysis is in
[`user-report-2026-09-09-ANALYSIS.md`](user-report-2026-09-09-ANALYSIS.md).

**Attachment referenced but not available to this analysis:** the reporter's debug
output, and the dual-motor demo they ran.

---

## Reporter's hardware

| Item | Value |
| --- | --- |
| Platform | "Large robot", built per the Parallax heavy-duty robot article |
| Motors | 2 × 6.5 inch hub motors (Parallax **27860**) |
| Battery | **18.5 V 5000 mAh 5S LiPo** |
| Motor driver | Universal Motor Driver **64010** |
| P2 module | Edge module **P2-EC Rev D** |
| Breakout | Mini board **64019** |
| Reference | https://www.parallax.com/build-a-heavy-duty-robot-using-brushless-dc-motors/ |

---

## Message (verbatim)

> I am seeking some assistance with a problem I have with running a spin2 large robot
> demo. The large robot is built according to the information provided on the Parallax
> website (https://www.parallax.com/build-a-heavy-duty-robot-using-brushless-dc-motors/).
> I ran the robot based on the demo programs on your website and cannot get consistent
> and repeatable runs of the demonstration. The motor on the right side typically does
> not operate consistently due to fault error, as shown in the debug output attached to
> this note. The fault can also occur with the left motor. Is there a known reason for
> this fault problem? I would appreciate any advice on the issue.
>
> The large robot has two 6.5 inch hub motors (27860) powered by an 18.5 V 5000Mah 5S
> Lipo battery. The motor operates from the Universal motor driver (64010), and
> controlled by edge module P2-EC Rev.D in the mini board 64019.
>
> I found that the dual motor demo (attached) will execute and wheels will spin as
> expected using a fully charged battery (18.5V) but subsequent repetitions on the demo
> typically shows fault on the right motor while the demo operates only the left motor.
> I have run simple tests to show the boards are operating properly using the Hello World
> demo, and have run both motors satisfactorily using the single motor demo program. Any
> insight on this problem would be appreciated.

---

## The five observations, isolated

Numbered for reference from the analysis document.

1. **Dual-motor demo faults; single-motor demo does not** — both motors run
   satisfactorily one at a time.
2. **The right motor faults far more often than the left**, but the left can fault too.
3. **First run on a fully charged battery works**; subsequent repetitions fault.
4. **After the right motor faults, the demo carries on driving only the left motor** —
   it does not stop, and evidently does not report the fault.
5. Hardware is otherwise sound — "Hello World" and single-motor demos both pass.
