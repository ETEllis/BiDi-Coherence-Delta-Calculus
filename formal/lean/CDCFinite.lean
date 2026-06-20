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

end CDCFinite
