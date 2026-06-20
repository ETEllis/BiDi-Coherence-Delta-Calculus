import Std

namespace CDCFinite

inductive Trit where
  | neg
  | zero
  | pos
  deriving DecidableEq, Repr

def Trit.value : Trit -> Int
  | Trit.neg => -1
  | Trit.zero => 0
  | Trit.pos => 1

def Trit.isZero : Trit -> Bool
  | Trit.zero => true
  | _ => false

def allTrits : Nat -> List (List Trit)
  | 0 => [[]]
  | n + 1 =>
      List.flatMap
        (fun xs => [Trit.neg :: xs, Trit.zero :: xs, Trit.pos :: xs])
        (allTrits n)

def prefixOKAux : Int -> List Trit -> Bool
  | _, [] => true
  | acc, x :: xs =>
      let next := acc + x.value
      (0 <= next) && prefixOKAux next xs

def prefixOK (xs : List Trit) : Bool :=
  prefixOKAux 0 xs

def sumTrits : List Trit -> Int
  | [] => 0
  | x :: xs => x.value + sumTrits xs

def hasZero (xs : List Trit) : Bool :=
  xs.any Trit.isZero

def total6 : Nat :=
  (allTrits 6).length

def admissible6 : Nat :=
  ((allTrits 6).filter prefixOK).length

def localized6 : Nat :=
  ((allTrits 6).filter fun xs => prefixOK xs && (sumTrits xs == 0)).length

def saturated6 : Nat :=
  ((allTrits 6).filter fun xs => prefixOK xs && !(hasZero xs)).length

def catalan6 : Nat :=
  ((allTrits 6).filter fun xs => prefixOK xs && (sumTrits xs == 0) && !(hasZero xs)).length

example : total6 = 729 := by native_decide
example : admissible6 = 267 := by native_decide
example : localized6 = 51 := by native_decide
example : saturated6 = 20 := by native_decide
example : catalan6 = 5 := by native_decide

def carrier3 : List Nat :=
  [0, 1, 2]

def mod3 (n : Nat) : Nat :=
  n % 3

def gate (a b : Nat) : Nat :=
  mod3 (a + b)

def inv3 (a : Nat) : Nat :=
  mod3 (3 - mod3 a)

def interfere (a b : Nat) : Nat :=
  mod3 (a + b)

def rotate (phi x : Nat) : Nat :=
  if mod3 phi == 1 then inv3 x else mod3 x

def all3 (p : Nat -> Bool) : Bool :=
  List.all carrier3 p

def all3₂ (p : Nat -> Nat -> Bool) : Bool :=
  all3 fun a => all3 fun b => p a b

def all3₃ (p : Nat -> Nat -> Nat -> Bool) : Bool :=
  all3 fun a => all3 fun b => all3 fun c => p a b c

def gateAssoc : Bool :=
  all3₃ fun a b c => gate (gate a b) c == gate a (gate b c)

def gateComm : Bool :=
  all3₂ fun a b => gate a b == gate b a

def gateIdentity : Bool :=
  all3 fun a => (gate a 0 == a) && (gate 0 a == a)

def gateInverse : Bool :=
  all3 fun a => gate a (inv3 a) == 0

def interfereAssoc : Bool :=
  all3₃ fun a b c => interfere (interfere a b) c == interfere a (interfere b c)

def interfereComm : Bool :=
  all3₂ fun a b => interfere a b == interfere b a

def interfereUnit : Bool :=
  all3 fun a => (interfere a 0 == a) && (interfere 0 a == a)

def rotationLinear : Bool :=
  all3₃ fun phi a b => rotate phi (interfere a b) == interfere (rotate phi a) (rotate phi b)

example : gateAssoc = true := by native_decide
example : gateComm = true := by native_decide
example : gateIdentity = true := by native_decide
example : gateInverse = true := by native_decide
example : interfereAssoc = true := by native_decide
example : interfereComm = true := by native_decide
example : interfereUnit = true := by native_decide
example : rotationLinear = true := by native_decide

def gateCarrier : Trit -> Trit -> Trit
  | Trit.neg, Trit.neg => Trit.pos
  | Trit.neg, Trit.zero => Trit.neg
  | Trit.neg, Trit.pos => Trit.zero
  | Trit.zero, Trit.neg => Trit.neg
  | Trit.zero, Trit.zero => Trit.zero
  | Trit.zero, Trit.pos => Trit.pos
  | Trit.pos, Trit.neg => Trit.zero
  | Trit.pos, Trit.zero => Trit.pos
  | Trit.pos, Trit.pos => Trit.neg

def invCarrier : Trit -> Trit
  | Trit.neg => Trit.pos
  | Trit.zero => Trit.zero
  | Trit.pos => Trit.neg

def interfereCarrier : Trit -> Trit -> Trit :=
  gateCarrier

def rotateCarrier : Trit -> Trit -> Trit
  | Trit.pos, x => invCarrier x
  | Trit.neg, x => x
  | Trit.zero, x => x

theorem gateCarrier_assoc (a b c : Trit) :
    gateCarrier (gateCarrier a b) c = gateCarrier a (gateCarrier b c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem gateCarrier_comm (a b : Trit) :
    gateCarrier a b = gateCarrier b a := by
  cases a <;> cases b <;> rfl

theorem gateCarrier_identity_left (a : Trit) :
    gateCarrier Trit.zero a = a := by
  cases a <;> rfl

theorem gateCarrier_identity_right (a : Trit) :
    gateCarrier a Trit.zero = a := by
  cases a <;> rfl

theorem gateCarrier_inverse_left (a : Trit) :
    gateCarrier (invCarrier a) a = Trit.zero := by
  cases a <;> rfl

theorem gateCarrier_inverse_right (a : Trit) :
    gateCarrier a (invCarrier a) = Trit.zero := by
  cases a <;> rfl

theorem interfereCarrier_assoc (a b c : Trit) :
    interfereCarrier (interfereCarrier a b) c = interfereCarrier a (interfereCarrier b c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem interfereCarrier_comm (a b : Trit) :
    interfereCarrier a b = interfereCarrier b a := by
  cases a <;> cases b <;> rfl

theorem interfereCarrier_identity_left (a : Trit) :
    interfereCarrier Trit.zero a = a := by
  cases a <;> rfl

theorem interfereCarrier_identity_right (a : Trit) :
    interfereCarrier a Trit.zero = a := by
  cases a <;> rfl

theorem rotateCarrier_linear (phi a b : Trit) :
    rotateCarrier phi (interfereCarrier a b)
      = interfereCarrier (rotateCarrier phi a) (rotateCarrier phi b) := by
  cases phi <;> cases a <;> cases b <;> rfl

end CDCFinite
