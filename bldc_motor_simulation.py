#!/usr/bin/env python3
"""
3상 BLDC 모터 시뮬레이션 (3-Phase BLDC Motor Simulation)

이 모듈은 브러시리스 DC 모터의 동작을 시뮬레이션합니다:
- 3상 역기전력 (Back-EMF) 파형
- 홀 센서 신호
- 3상 전류 파형
- 모터 토크 및 속도 응답
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class BLDCMotorParams:
    """BLDC 모터 파라미터"""
    # 전기적 파라미터
    R: float = 0.5          # 상저항 (Ohm)
    L: float = 0.001        # 상인덕턴스 (H)
    Ke: float = 0.01        # 역기전력 상수 (V/rad/s)
    Kt: float = 0.01        # 토크 상수 (Nm/A)

    # 기계적 파라미터
    J: float = 0.0001       # 관성 모멘트 (kg·m²)
    B: float = 0.001        # 점성 마찰 계수 (Nm·s/rad)
    pole_pairs: int = 4     # 극쌍 수

    # 전원 파라미터
    Vdc: float = 24.0       # DC 링크 전압 (V)


class BLDCMotorSimulator:
    """3상 BLDC 모터 시뮬레이터"""

    def __init__(self, params: Optional[BLDCMotorParams] = None):
        self.params = params or BLDCMotorParams()
        self.reset()

    def reset(self):
        """시뮬레이션 상태 초기화"""
        self.theta_e = 0.0      # 전기각 (rad)
        self.omega = 0.0        # 기계적 각속도 (rad/s)
        self.theta_m = 0.0      # 기계적 각도 (rad)
        self.i_a = 0.0          # A상 전류
        self.i_b = 0.0          # B상 전류
        self.i_c = 0.0          # C상 전류

    def trapezoidal_bemf(self, theta: float) -> float:
        """
        사다리꼴 역기전력 파형 생성

        Args:
            theta: 전기각 (rad)

        Returns:
            정규화된 역기전력 값 (-1 ~ 1)
        """
        theta = theta % (2 * np.pi)

        # 사다리꼴 파형 정의 (120도 전도 방식)
        if theta < np.pi / 6:
            return 6 * theta / np.pi
        elif theta < 5 * np.pi / 6:
            return 1.0
        elif theta < 7 * np.pi / 6:
            return 1.0 - 6 * (theta - 5 * np.pi / 6) / np.pi
        elif theta < 11 * np.pi / 6:
            return -1.0
        else:
            return -1.0 + 6 * (theta - 11 * np.pi / 6) / np.pi

    def get_bemf(self, theta_e: float, omega: float) -> Tuple[float, float, float]:
        """
        3상 역기전력 계산

        Args:
            theta_e: 전기각 (rad)
            omega: 기계적 각속도 (rad/s)

        Returns:
            (e_a, e_b, e_c): 3상 역기전력
        """
        Ke = self.params.Ke
        p = self.params.pole_pairs
        omega_e = omega * p  # 전기적 각속도

        e_a = Ke * omega_e * self.trapezoidal_bemf(theta_e)
        e_b = Ke * omega_e * self.trapezoidal_bemf(theta_e - 2 * np.pi / 3)
        e_c = Ke * omega_e * self.trapezoidal_bemf(theta_e + 2 * np.pi / 3)

        return e_a, e_b, e_c

    def get_hall_signals(self, theta_e: float) -> Tuple[int, int, int]:
        """
        홀 센서 신호 생성 (120도 간격)

        Args:
            theta_e: 전기각 (rad)

        Returns:
            (H1, H2, H3): 홀 센서 신호 (0 또는 1)
        """
        theta = theta_e % (2 * np.pi)

        # 홀 센서 A (0 ~ 180도에서 High)
        H1 = 1 if 0 <= theta < np.pi else 0

        # 홀 센서 B (120도 지연, 60 ~ 240도에서 High)
        H2 = 1 if np.pi / 3 <= theta < 4 * np.pi / 3 else 0

        # 홀 센서 C (240도 지연, 180 ~ 360도에서 High)
        H3 = 1 if 2 * np.pi / 3 <= theta < 5 * np.pi / 3 else 0

        return H1, H2, H3

    def get_commutation_state(self, H1: int, H2: int, H3: int) -> int:
        """
        홀 센서 신호로부터 정류 상태 결정

        Returns:
            정류 상태 (1-6)
        """
        hall_state = (H1 << 2) | (H2 << 1) | H3

        # 홀 센서 상태 -> 정류 상태 매핑
        commutation_table = {
            0b101: 1,  # A+ B-
            0b100: 2,  # A+ C-
            0b110: 3,  # B+ C-
            0b010: 4,  # B+ A-
            0b011: 5,  # C+ A-
            0b001: 6,  # C+ B-
        }

        return commutation_table.get(hall_state, 0)

    def get_phase_voltages(self, comm_state: int, Vdc: float) -> Tuple[float, float, float]:
        """
        정류 상태에 따른 상전압 결정

        Args:
            comm_state: 정류 상태 (1-6)
            Vdc: DC 링크 전압

        Returns:
            (V_a, V_b, V_c): 3상 전압
        """
        # 정류 상태별 스위칭 패턴
        voltage_patterns = {
            1: (Vdc, -Vdc, 0),      # A+ B-
            2: (Vdc, 0, -Vdc),      # A+ C-
            3: (0, Vdc, -Vdc),      # B+ C-
            4: (-Vdc, Vdc, 0),      # B+ A-
            5: (-Vdc, 0, Vdc),      # C+ A-
            6: (0, -Vdc, Vdc),      # C+ B-
        }

        return voltage_patterns.get(comm_state, (0, 0, 0))

    def simulate(self, t_end: float, dt: float = 1e-5,
                 T_load: float = 0.0) -> dict:
        """
        BLDC 모터 시뮬레이션 실행

        Args:
            t_end: 시뮬레이션 종료 시간 (s)
            dt: 시간 스텝 (s)
            T_load: 부하 토크 (Nm)

        Returns:
            시뮬레이션 결과 딕셔너리
        """
        # 시뮬레이션 파라미터
        p = self.params
        n_steps = int(t_end / dt)

        # 결과 저장 배열
        time = np.zeros(n_steps)
        omega_hist = np.zeros(n_steps)
        theta_e_hist = np.zeros(n_steps)
        theta_m_hist = np.zeros(n_steps)

        i_a_hist = np.zeros(n_steps)
        i_b_hist = np.zeros(n_steps)
        i_c_hist = np.zeros(n_steps)

        e_a_hist = np.zeros(n_steps)
        e_b_hist = np.zeros(n_steps)
        e_c_hist = np.zeros(n_steps)

        v_a_hist = np.zeros(n_steps)
        v_b_hist = np.zeros(n_steps)
        v_c_hist = np.zeros(n_steps)

        H1_hist = np.zeros(n_steps)
        H2_hist = np.zeros(n_steps)
        H3_hist = np.zeros(n_steps)

        torque_hist = np.zeros(n_steps)
        rpm_hist = np.zeros(n_steps)

        # 상태 변수 초기화
        self.reset()

        # 시뮬레이션 루프
        for i in range(n_steps):
            time[i] = i * dt

            # 역기전력 계산
            e_a, e_b, e_c = self.get_bemf(self.theta_e, self.omega)

            # 홀 센서 신호
            H1, H2, H3 = self.get_hall_signals(self.theta_e)

            # 정류 상태 및 상전압
            comm_state = self.get_commutation_state(H1, H2, H3)
            v_a, v_b, v_c = self.get_phase_voltages(comm_state, p.Vdc)

            # 전류 미분 방정식 (di/dt = (V - e - R*i) / L)
            di_a = (v_a - e_a - p.R * self.i_a) / p.L
            di_b = (v_b - e_b - p.R * self.i_b) / p.L
            di_c = (v_c - e_c - p.R * self.i_c) / p.L

            # 전류 업데이트 (오일러 방법)
            self.i_a += di_a * dt
            self.i_b += di_b * dt
            self.i_c += di_c * dt

            # 전자기 토크 계산 (T_e = Kt * (e_a*i_a + e_b*i_b + e_c*i_c) / omega)
            if abs(self.omega) > 0.1:
                T_e = (e_a * self.i_a + e_b * self.i_b + e_c * self.i_c) / self.omega
            else:
                T_e = p.Kt * (self.i_a + self.i_b + self.i_c)

            # 기계적 동역학 (J * dω/dt = T_e - B*ω - T_load)
            domega = (T_e - p.B * self.omega - T_load) / p.J
            self.omega += domega * dt
            self.omega = max(0, self.omega)  # 역회전 방지

            # 각도 업데이트
            self.theta_m += self.omega * dt
            self.theta_e = self.theta_m * p.pole_pairs

            # 결과 저장
            omega_hist[i] = self.omega
            theta_e_hist[i] = self.theta_e % (2 * np.pi)
            theta_m_hist[i] = self.theta_m

            i_a_hist[i] = self.i_a
            i_b_hist[i] = self.i_b
            i_c_hist[i] = self.i_c

            e_a_hist[i] = e_a
            e_b_hist[i] = e_b
            e_c_hist[i] = e_c

            v_a_hist[i] = v_a
            v_b_hist[i] = v_b
            v_c_hist[i] = v_c

            H1_hist[i] = H1
            H2_hist[i] = H2
            H3_hist[i] = H3

            torque_hist[i] = T_e
            rpm_hist[i] = self.omega * 60 / (2 * np.pi)

        return {
            'time': time,
            'omega': omega_hist,
            'theta_e': theta_e_hist,
            'theta_m': theta_m_hist,
            'i_a': i_a_hist,
            'i_b': i_b_hist,
            'i_c': i_c_hist,
            'e_a': e_a_hist,
            'e_b': e_b_hist,
            'e_c': e_c_hist,
            'v_a': v_a_hist,
            'v_b': v_b_hist,
            'v_c': v_c_hist,
            'H1': H1_hist,
            'H2': H2_hist,
            'H3': H3_hist,
            'torque': torque_hist,
            'rpm': rpm_hist,
        }


def plot_simulation_results(results: dict, save_path: Optional[str] = None):
    """
    시뮬레이션 결과 시각화

    Args:
        results: 시뮬레이션 결과 딕셔너리
        save_path: 저장 경로 (선택사항)
    """
    time = results['time'] * 1000  # ms로 변환

    fig, axes = plt.subplots(5, 1, figsize=(14, 16))
    fig.suptitle('3상 BLDC 모터 시뮬레이션 결과', fontsize=14, fontweight='bold')

    # 1. 모터 속도 (RPM)
    axes[0].plot(time, results['rpm'], 'b-', linewidth=1.5)
    axes[0].set_ylabel('속도 (RPM)')
    axes[0].set_title('모터 회전 속도')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([time[0], time[-1]])

    # 2. 3상 역기전력 (Back-EMF)
    axes[1].plot(time, results['e_a'], 'r-', label='Phase A', linewidth=1)
    axes[1].plot(time, results['e_b'], 'g-', label='Phase B', linewidth=1)
    axes[1].plot(time, results['e_c'], 'b-', label='Phase C', linewidth=1)
    axes[1].set_ylabel('Back-EMF (V)')
    axes[1].set_title('3상 역기전력 파형 (사다리꼴)')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([time[0], time[-1]])

    # 3. 3상 전류
    axes[2].plot(time, results['i_a'], 'r-', label='Phase A', linewidth=1)
    axes[2].plot(time, results['i_b'], 'g-', label='Phase B', linewidth=1)
    axes[2].plot(time, results['i_c'], 'b-', label='Phase C', linewidth=1)
    axes[2].set_ylabel('전류 (A)')
    axes[2].set_title('3상 전류 파형')
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim([time[0], time[-1]])

    # 4. 홀 센서 신호
    offset = 0
    axes[3].fill_between(time, offset, results['H1'] * 0.8 + offset,
                         alpha=0.7, label='Hall A', color='red')
    offset += 1
    axes[3].fill_between(time, offset, results['H2'] * 0.8 + offset,
                         alpha=0.7, label='Hall B', color='green')
    offset += 1
    axes[3].fill_between(time, offset, results['H3'] * 0.8 + offset,
                         alpha=0.7, label='Hall C', color='blue')
    axes[3].set_ylabel('홀 센서')
    axes[3].set_title('홀 센서 신호 (120도 간격)')
    axes[3].set_yticks([0.4, 1.4, 2.4])
    axes[3].set_yticklabels(['H1', 'H2', 'H3'])
    axes[3].legend(loc='upper right')
    axes[3].grid(True, alpha=0.3, axis='x')
    axes[3].set_xlim([time[0], time[-1]])

    # 5. 토크
    axes[4].plot(time, results['torque'], 'm-', linewidth=1)
    axes[4].set_ylabel('토크 (Nm)')
    axes[4].set_xlabel('시간 (ms)')
    axes[4].set_title('전자기 토크')
    axes[4].grid(True, alpha=0.3)
    axes[4].set_xlim([time[0], time[-1]])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"그래프가 '{save_path}'에 저장되었습니다.")

    plt.show()


def plot_steady_state(results: dict, start_time: float = 0.04,
                      duration: float = 0.01, save_path: Optional[str] = None):
    """
    정상 상태에서의 파형 확대 표시

    Args:
        results: 시뮬레이션 결과
        start_time: 시작 시간 (s)
        duration: 표시 기간 (s)
        save_path: 저장 경로
    """
    time = results['time']
    dt = time[1] - time[0]

    start_idx = int(start_time / dt)
    end_idx = int((start_time + duration) / dt)

    t_ms = time[start_idx:end_idx] * 1000

    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    fig.suptitle('정상 상태 파형 (확대)', fontsize=14, fontweight='bold')

    # 역기전력
    axes[0].plot(t_ms, results['e_a'][start_idx:end_idx], 'r-',
                 label='Phase A', linewidth=2)
    axes[0].plot(t_ms, results['e_b'][start_idx:end_idx], 'g-',
                 label='Phase B', linewidth=2)
    axes[0].plot(t_ms, results['e_c'][start_idx:end_idx], 'b-',
                 label='Phase C', linewidth=2)
    axes[0].set_ylabel('Back-EMF (V)')
    axes[0].set_title('3상 역기전력')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)

    # 전류
    axes[1].plot(t_ms, results['i_a'][start_idx:end_idx], 'r-',
                 label='Phase A', linewidth=2)
    axes[1].plot(t_ms, results['i_b'][start_idx:end_idx], 'g-',
                 label='Phase B', linewidth=2)
    axes[1].plot(t_ms, results['i_c'][start_idx:end_idx], 'b-',
                 label='Phase C', linewidth=2)
    axes[1].set_ylabel('전류 (A)')
    axes[1].set_title('3상 전류')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)

    # 홀 센서
    offset = 0
    axes[2].fill_between(t_ms, offset,
                         results['H1'][start_idx:end_idx] * 0.8 + offset,
                         alpha=0.7, label='Hall A', color='red')
    offset += 1
    axes[2].fill_between(t_ms, offset,
                         results['H2'][start_idx:end_idx] * 0.8 + offset,
                         alpha=0.7, label='Hall B', color='green')
    offset += 1
    axes[2].fill_between(t_ms, offset,
                         results['H3'][start_idx:end_idx] * 0.8 + offset,
                         alpha=0.7, label='Hall C', color='blue')
    axes[2].set_ylabel('홀 센서')
    axes[2].set_xlabel('시간 (ms)')
    axes[2].set_title('홀 센서 신호')
    axes[2].set_yticks([0.4, 1.4, 2.4])
    axes[2].set_yticklabels(['H1', 'H2', 'H3'])
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"그래프가 '{save_path}'에 저장되었습니다.")

    plt.show()


def print_motor_specs(params: BLDCMotorParams):
    """모터 사양 출력"""
    print("\n" + "=" * 50)
    print("       BLDC 모터 사양")
    print("=" * 50)
    print(f"  상 저항 (R):           {params.R:.3f} Ω")
    print(f"  상 인덕턴스 (L):       {params.L * 1000:.3f} mH")
    print(f"  역기전력 상수 (Ke):    {params.Ke:.4f} V/(rad/s)")
    print(f"  토크 상수 (Kt):        {params.Kt:.4f} Nm/A")
    print(f"  관성 모멘트 (J):       {params.J * 1e6:.2f} g·cm²")
    print(f"  마찰 계수 (B):         {params.B:.4f} Nm·s/rad")
    print(f"  극쌍 수:               {params.pole_pairs}")
    print(f"  DC 링크 전압:          {params.Vdc:.1f} V")
    print("=" * 50 + "\n")


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("    3상 BLDC 모터 시뮬레이션")
    print("    (3-Phase BLDC Motor Simulation)")
    print("=" * 60)

    # 모터 파라미터 설정
    params = BLDCMotorParams(
        R=0.5,              # 상 저항 (Ohm)
        L=0.001,            # 상 인덕턴스 (H)
        Ke=0.01,            # 역기전력 상수
        Kt=0.01,            # 토크 상수
        J=0.0001,           # 관성 모멘트
        B=0.001,            # 마찰 계수
        pole_pairs=4,       # 극쌍 수
        Vdc=24.0            # DC 전압
    )

    # 모터 사양 출력
    print_motor_specs(params)

    # 시뮬레이터 생성 및 실행
    print("시뮬레이션 실행 중...")
    simulator = BLDCMotorSimulator(params)
    results = simulator.simulate(
        t_end=0.05,         # 50ms 시뮬레이션
        dt=1e-6,            # 1us 시간 스텝
        T_load=0.001        # 1mNm 부하
    )

    # 결과 요약
    final_rpm = results['rpm'][-1]
    max_current = max(
        max(abs(results['i_a'])),
        max(abs(results['i_b'])),
        max(abs(results['i_c']))
    )
    avg_torque = np.mean(results['torque'][-1000:])

    print("\n시뮬레이션 완료!")
    print("-" * 40)
    print(f"  최종 속도:     {final_rpm:.1f} RPM")
    print(f"  최대 전류:     {max_current:.2f} A")
    print(f"  평균 토크:     {avg_torque * 1000:.3f} mNm")
    print("-" * 40)

    # 결과 시각화
    print("\n그래프를 생성합니다...")
    plot_simulation_results(results, save_path='bldc_simulation_full.png')
    plot_steady_state(results, start_time=0.04, duration=0.008,
                      save_path='bldc_simulation_steady.png')

    return results


if __name__ == '__main__':
    results = main()
