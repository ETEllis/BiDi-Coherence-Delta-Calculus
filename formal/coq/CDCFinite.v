From Stdlib Require Import Bool.Bool.
From Stdlib Require Import Lists.List.
From Stdlib Require Import Arith.PeanoNat.
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

Definition carrier3 : list nat :=
  [0%nat; 1%nat; 2%nat].

Definition mod3 (n : nat) : nat :=
  Nat.modulo n 3.

Definition gate (a b : nat) : nat :=
  mod3 ((a + b)%nat).

Definition inv3 (a : nat) : nat :=
  mod3 ((3 - mod3 a)%nat).

Definition interfere (a b : nat) : nat :=
  mod3 ((a + b)%nat).

Definition rotate (phi x : nat) : nat :=
  if Nat.eqb (mod3 phi) 1 then inv3 x else mod3 x.

Definition all3 (p : nat -> bool) : bool :=
  forallb p carrier3.

Definition all3_2 (p : nat -> nat -> bool) : bool :=
  all3 (fun a => all3 (fun b => p a b)).

Definition all3_3 (p : nat -> nat -> nat -> bool) : bool :=
  all3 (fun a => all3 (fun b => all3 (fun c => p a b c))).

Definition gate_assoc : bool :=
  all3_3 (fun a b c => Nat.eqb (gate (gate a b) c) (gate a (gate b c))).

Definition gate_comm : bool :=
  all3_2 (fun a b => Nat.eqb (gate a b) (gate b a)).

Definition gate_identity : bool :=
  all3 (fun a => Nat.eqb (gate a 0) a && Nat.eqb (gate 0 a) a).

Definition gate_inverse : bool :=
  all3 (fun a => Nat.eqb (gate a (inv3 a)) 0).

Definition interfere_assoc : bool :=
  all3_3 (fun a b c => Nat.eqb (interfere (interfere a b) c) (interfere a (interfere b c))).

Definition interfere_comm : bool :=
  all3_2 (fun a b => Nat.eqb (interfere a b) (interfere b a)).

Definition interfere_unit : bool :=
  all3 (fun a => Nat.eqb (interfere a 0) a && Nat.eqb (interfere 0 a) a).

Definition rotation_linear : bool :=
  all3_3 (fun phi a b => Nat.eqb (rotate phi (interfere a b)) (interfere (rotate phi a) (rotate phi b))).

Example gate_assoc_checked : gate_assoc = true.
Proof. vm_compute. reflexivity. Qed.

Example gate_comm_checked : gate_comm = true.
Proof. vm_compute. reflexivity. Qed.

Example gate_identity_checked : gate_identity = true.
Proof. vm_compute. reflexivity. Qed.

Example gate_inverse_checked : gate_inverse = true.
Proof. vm_compute. reflexivity. Qed.

Example interfere_assoc_checked : interfere_assoc = true.
Proof. vm_compute. reflexivity. Qed.

Example interfere_comm_checked : interfere_comm = true.
Proof. vm_compute. reflexivity. Qed.

Example interfere_unit_checked : interfere_unit = true.
Proof. vm_compute. reflexivity. Qed.

Example rotation_linear_checked : rotation_linear = true.
Proof. vm_compute. reflexivity. Qed.

Definition gate_carrier (a b : trit) : trit :=
  match a, b with
  | Neg, Neg => Pos
  | Neg, Zero => Neg
  | Neg, Pos => Zero
  | Zero, Neg => Neg
  | Zero, Zero => Zero
  | Zero, Pos => Pos
  | Pos, Neg => Zero
  | Pos, Zero => Pos
  | Pos, Pos => Neg
  end.

Definition inv_carrier (a : trit) : trit :=
  match a with
  | Neg => Pos
  | Zero => Zero
  | Pos => Neg
  end.

Definition interfere_carrier : trit -> trit -> trit :=
  gate_carrier.

Definition rotate_carrier (phi x : trit) : trit :=
  match phi with
  | Pos => inv_carrier x
  | Neg => x
  | Zero => x
  end.

Theorem gate_carrier_assoc :
  forall a b c, gate_carrier (gate_carrier a b) c = gate_carrier a (gate_carrier b c).
Proof. intros [] [] []; reflexivity. Qed.

Theorem gate_carrier_comm :
  forall a b, gate_carrier a b = gate_carrier b a.
Proof. intros [] []; reflexivity. Qed.

Theorem gate_carrier_identity_left :
  forall a, gate_carrier Zero a = a.
Proof. intros []; reflexivity. Qed.

Theorem gate_carrier_identity_right :
  forall a, gate_carrier a Zero = a.
Proof. intros []; reflexivity. Qed.

Theorem gate_carrier_inverse_left :
  forall a, gate_carrier (inv_carrier a) a = Zero.
Proof. intros []; reflexivity. Qed.

Theorem gate_carrier_inverse_right :
  forall a, gate_carrier a (inv_carrier a) = Zero.
Proof. intros []; reflexivity. Qed.

Theorem interfere_carrier_assoc :
  forall a b c, interfere_carrier (interfere_carrier a b) c = interfere_carrier a (interfere_carrier b c).
Proof. intros [] [] []; reflexivity. Qed.

Theorem interfere_carrier_comm :
  forall a b, interfere_carrier a b = interfere_carrier b a.
Proof. intros [] []; reflexivity. Qed.

Theorem interfere_carrier_identity_left :
  forall a, interfere_carrier Zero a = a.
Proof. intros []; reflexivity. Qed.

Theorem interfere_carrier_identity_right :
  forall a, interfere_carrier a Zero = a.
Proof. intros []; reflexivity. Qed.

Theorem rotate_carrier_linear :
  forall phi a b,
    rotate_carrier phi (interfere_carrier a b)
    = interfere_carrier (rotate_carrier phi a) (rotate_carrier phi b).
Proof. intros [] [] []; reflexivity. Qed.
