From Stdlib Require Import Bool.Bool.
From Stdlib Require Import Lists.List.
From Stdlib Require Import ZArith.ZArith.
Import ListNotations.
Open Scope Z_scope.

Inductive trit : Set :=
| Neg
| Zero
| Pos.

Definition trit_value (t : trit) : Z :=
  match t with
  | Neg => -1
  | Zero => 0
  | Pos => 1
  end.

Definition trit_is_zero (t : trit) : bool :=
  match t with
  | Zero => true
  | _ => false
  end.

Fixpoint all_trits (n : nat) : list (list trit) :=
  match n with
  | O => [[]]
  | S n' =>
      concat
        (map
          (fun xs => [Neg :: xs; Zero :: xs; Pos :: xs])
          (all_trits n'))
  end.

Fixpoint prefix_ok_aux (acc : Z) (xs : list trit) : bool :=
  match xs with
  | [] => true
  | x :: rest =>
      let next := acc + trit_value x in
      (0 <=? next) && prefix_ok_aux next rest
  end.

Definition prefix_ok (xs : list trit) : bool :=
  prefix_ok_aux 0 xs.

Fixpoint sum_trits (xs : list trit) : Z :=
  match xs with
  | [] => 0
  | x :: rest => trit_value x + sum_trits rest
  end.

Definition has_zero (xs : list trit) : bool :=
  existsb trit_is_zero xs.

Definition total6 : nat :=
  length (all_trits 6).

Definition admissible6 : nat :=
  length (filter prefix_ok (all_trits 6)).

Definition localized6 : nat :=
  length (filter (fun xs => prefix_ok xs && (sum_trits xs =? 0)) (all_trits 6)).

Definition saturated6 : nat :=
  length (filter (fun xs => prefix_ok xs && negb (has_zero xs)) (all_trits 6)).

Definition catalan6 : nat :=
  length (filter (fun xs => prefix_ok xs && (sum_trits xs =? 0) && negb (has_zero xs)) (all_trits 6)).

Example total6_checked : total6 = 729%nat.
Proof. vm_compute. reflexivity. Qed.

Example admissible6_checked : admissible6 = 267%nat.
Proof. vm_compute. reflexivity. Qed.

Example localized6_checked : localized6 = 51%nat.
Proof. vm_compute. reflexivity. Qed.

Example saturated6_checked : saturated6 = 20%nat.
Proof. vm_compute. reflexivity. Qed.

Example catalan6_checked : catalan6 = 5%nat.
Proof. vm_compute. reflexivity. Qed.
