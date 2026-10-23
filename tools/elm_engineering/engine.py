"""Dependency-free educational simulations, not hardware control or payments."""

import math


def _require_finite(**values: float) -> None:
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite real number.")
        try:
            finite = math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError(f"{name} must be a finite real number.")


class ELM369EngineeringCore:
    def __init__(self, project_id="JMR0824197846902"):
        self.project_id = project_id
        self.charity_fee_rate = 0.01

    def compute_2d_inverse_kinematics(
        self, x: float, y: float, l1: float, l2: float
    ):
        """Return the positive-theta2 solution in degrees for a planar two-link arm."""
        _require_finite(x=x, y=y, l1=l1, l2=l2)
        if l1 <= 0 or l2 <= 0:
            raise ValueError("Link lengths must be positive.")

        # Normalize before squaring to avoid overflow at large coordinate scales.
        scale = max(abs(x), abs(y), l1, l2)
        nx, ny, a, b = x / scale, y / scale, l1 / scale, l2 / scale
        radius = math.hypot(nx, ny)
        inner, outer = abs(a - b), a + b
        # Independent normalization can shift an exact boundary by a few ulps.
        beyond_outer = radius > outer and not math.isclose(radius, outer, rel_tol=1e-15)
        inside_inner = radius < inner and not math.isclose(radius, inner, rel_tol=1e-15)
        if beyond_outer or inside_inner:
            return {"error": "Target position is outside the robotic workspace boundary."}
        denominator = 2 * a * b
        if denominator == 0:
            raise ValueError("Link length ratio exceeds floating-point resolution.")
        cos_theta2 = (radius * radius - a * a - b * b) / denominator
        theta_2 = math.acos(max(-1.0, min(1.0, cos_theta2)))
        if radius == 0:
            theta_1 = 0.0
        else:
            theta_1 = math.atan2(y, x) - math.atan2(
                b * math.sin(theta_2), a + b * math.cos(theta_2)
            )
        return {
            "theta_1_deg": round(math.degrees(theta_1), 2),
            "theta_2_deg": round(math.degrees(theta_2), 2),
            "status": "KINEMATICS_SOLVED_SUCCESSFULLY",
        }

    def simulate_pid_control_step(
        self, setpoint: float, current_value: float, kp: float, ki: float,
        kd: float, dt: float, error_integral: float, previous_error: float,
    ):
        """Compute an unsaturated PID step; retain full precision in feedback state."""
        _require_finite(
            setpoint=setpoint, current_value=current_value, kp=kp, ki=ki,
            kd=kd, dt=dt, error_integral=error_integral,
            previous_error=previous_error,
        )
        if dt <= 0:
            raise ValueError("dt must be positive.")
        error = setpoint - current_value
        integral = error_integral + error * dt
        derivative = (error - previous_error) / dt
        output = kp * error + ki * integral + kd * derivative
        _require_finite(
            current_error=error, new_integral=integral,
            derivative=derivative, control_signal=output,
        )
        return {
            "control_signal": round(output, 4),
            "new_integral": integral,
            "current_error": error,
        }

    def evaluate_project_resource_allocation(self, gross_simulation_value: float):
        """Model the 1% allocation; no money is transferred or donated."""
        _require_finite(gross_simulation_value=gross_simulation_value)
        if gross_simulation_value < 0:
            raise ValueError("gross_simulation_value must be nonnegative.")
        charity_deduction = gross_simulation_value * self.charity_fee_rate
        return {
            "gross_value": gross_simulation_value,
            "charity_allocation": charity_deduction,
            "net_retained_resource": gross_simulation_value - charity_deduction,
            "charity_targets": [
                "Shriners", "Cancer/Stroke Research", "Human Trafficking Prevention"
            ],
        }
