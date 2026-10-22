# Diary study, March 2025 — date entry at reception

14 reception staff, two weeks, Harbour Clinic and Leith Walk Annexe.

Reception staff enter appointment dates on behalf of patients who phone in; the patient-facing booking
form is the same component. Staff type dates from habit in ISO `yyyy-mm-dd`, because that is the format
on the health board's own exchange forms, and 12 of 14 said a picker slowed them down for dates they
already knew.

We trialled lenient parsing (accepting `dd/mm/yyyy` and `mm/dd/yyyy` alongside ISO) for six weeks in
late 2024 and withdrew it: three appointments were booked on the wrong day because an ambiguous date
such as `03/11/2026` was parsed to the US order. A mis-booked clinical appointment is a reportable
safety incident, so the form now **rejects** anything that is not ISO rather than guessing between
orders. The rejection is deliberate, not an oversight, and it is the reason we do not normalise here.

Reviewed 2026-02; no change.
