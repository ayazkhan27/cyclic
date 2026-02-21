import Mathlib.Data.ZMod.Basic

variable (p : ℕ) [Fact p.Prime] (hp2 : p > 2)

theorem sum_of_residues_zero : (∑ x : ZMod p, x) = 0 := by
  have h_sum : ∑ x : ZMod p, x = ∑ x : ZMod p, -x := by
    apply Equiv.sum_comp (Equiv.neg (ZMod p)) id

  have h : (2 : ZMod p) * (∑ x : ZMod p, x) = 0 := by
    calc (2 : ZMod p) * ∑ x : ZMod p, x
      _ = ∑ x : ZMod p, x + ∑ x : ZMod p, x := by ring
      _ = ∑ x : ZMod p, x + ∑ x : ZMod p, -x := by rw [h_sum]
      _ = ∑ x : ZMod p, (x + -x) := by rw [← Finset.sum_add_distrib]
      _ = ∑ x : ZMod p, 0 := by simp
      _ = 0 := by simp

  cases mul_eq_zero.mp h with
  | inl h2 =>
    exfalso
    revert h2
    intro h2_eq
    have h_val : (2 : ZMod p).val = 2 % p := by rfl
    have h_mod : 2 % p = 2 := Nat.mod_eq_of_lt hp2
    rw [h_mod] at h_val
    have h_zero : (2 : ZMod p).val = 0 := by rw [h2_eq, ZMod.val_zero]
    linarith
  | inr h_ans => exact h_ans
