"""Run the supplied university engineering examples."""

from .engine import ELM369EngineeringCore


def main():
    core = ELM369EngineeringCore()
    ik_result = core.compute_2d_inverse_kinematics(15.0, 10.0, 12.0, 10.0)
    pid_result = core.simulate_pid_control_step(
        setpoint=210.0, current_value=205.5, kp=1.2, ki=0.05, kd=0.1,
        dt=0.1, error_integral=2.0, previous_error=5.0,
    )
    financial_model = core.evaluate_project_resource_allocation(10000.0)
    print("=== PROJECT ELM369 UNIVERSITY ENGINEERING ENGINE ONLINE ===")
    print(f"Robotics Inverse Kinematics: {ik_result}")
    print(f"Control Systems PID Step: {pid_result}")
    print(f"Governance & Charity Allocation: {financial_model}")


if __name__ == "__main__":
    main()
