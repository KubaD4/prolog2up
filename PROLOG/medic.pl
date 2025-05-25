% This file defines a medical protocol knowledge base in Prolog
%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Patients
patient(p1).
patient(p2).

% Medical Procedures
procedure(electrocardiogram).
procedure(blood_test).
procedure(x_ray).

% Medical Staff
staff(doctor1).
staff(nurse1).
staff(technician1).

% Resources
resource(equipment_ecg).
resource(equipment_xray).
resource(lab_blood_test).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
    needs_procedure(p1, electrocardiogram), needs_procedure(p1, blood_test),
    needs_procedure(p2, x_ray),
    available(doctor1), available(nurse1), available(technician1),
    available(equipment_ecg), available(equipment_xray), available(lab_blood_test)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
    procedure_done(p1, electrocardiogram), procedure_done(p1, blood_test),
    procedure_done(p2, x_ray),
    available(doctor1), available(nurse1), available(technician1),
    available(equipment_ecg), available(equipment_xray), available(lab_blood_test)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%
% Perform an electrocardiogram
action(perform_ecg(Staff, Patient),
    [needs_procedure(Patient, electrocardiogram), available(Staff), available(equipment_ecg)],
    [],
    [],
    [staff(Staff), patient(Patient)],
    [
        del(needs_procedure(Patient, electrocardiogram)), del(available(Staff)), del(available(equipment_ecg)),
        add(procedure_done(Patient, electrocardiogram)), add(available(Staff)), add(available(equipment_ecg))
    ]
).

% Perform a blood test
action(perform_blood_test(Staff, Patient),
    [needs_procedure(Patient, blood_test), available(Staff), available(lab_blood_test)],
    [],
    [],
    [staff(Staff), patient(Patient)],
    [
        del(needs_procedure(Patient, blood_test)), del(available(Staff)), del(available(lab_blood_test)),
        add(procedure_done(Patient, blood_test)), add(available(Staff)), add(available(lab_blood_test))
    ]
).

% Perform an X-ray
action(perform_xray(Staff, Patient),
    [needs_procedure(Patient, x_ray), available(Staff), available(equipment_xray)],
    [],
    [],
    [staff(Staff), patient(Patient)],
    [
        del(needs_procedure(Patient, x_ray)), del(available(Staff)), del(available(equipment_xray)),
        add(procedure_done(Patient, x_ray)), add(available(Staff)), add(available(equipment_xray))
    ]
).