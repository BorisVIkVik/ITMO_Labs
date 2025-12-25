import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
# from abc import ABC, abstractcalssmethod#, classmethod

def generate_banner(num):
    return Banner(num)    
class Banner:
    def __init__(self, num, color = None, prob = None) -> None:
        if prob is None:
            self.conversion_prob = np.random.random()
        else:
            self.conversion_prob = prob
        if color is None:
            self.color = tuple(np.random.random((3)))
        else:
            self.color = color
        self.num = num

    def click(self):
        if np.random.random() <= self.conversion_prob:
            return 1
        return 0

class Strategy():
    # @classmethod
    # @abstractmethod
    def __init__(self) -> None:
        pass

    # @classmethod
    # @abstractmethod
    def spin(self) -> bool:
        pass

    # @classmethod
    # @abstractmethod
    def add_banner(self, banner) -> None:
        pass

class EpsilonGreedy(Strategy):
    def __init__(self, eps):
        self.banners = []
        self.reward = []
        self.spin_count = []
        self.eps = eps

    def spin(self):
        if self.eps < np.random.random():
            mx = -1
            chosen_arm = 0
            for i in range(len(self.banners)):
                if mx < self.reward[i]:
                    mx = self.reward[i]
                    chosen_arm = i
            
        else:
            chosen_arm = np.random.randint(0, len(self.banners))
        self.calculate_reward(chosen_arm)


        # aproximate_banners_probability = [0] * len(self.banners)
        # for i, ban in enumerate(self.banners):
        #     aproximate_banners_probability[i] = ban.prob
        # return aproximate_banners_probability

    def add_banner(self, banner):
        self.banners.append(banner)
        self.reward.append(0.0)
        self.spin_count.append(0)

    def calculate_reward(self, chosen_arm):
        n = self.spin_count[chosen_arm] + 1
        self.spin_count[chosen_arm] = n
        val = self.reward[chosen_arm]
        self.reward[chosen_arm] = ((n - 1)/n) * val + (self.banners[chosen_arm].click() / n)




class Simulation:
    def __init__(self) -> None:
        self.banners =  []
        self.strategies = {}
        self.strategies['Greedy'] = EpsilonGreedy(0.5)
        pass

    def make_simulation(self, iterations):
        for i in range(iterations):
            for strat in self.strategies.values():
                strat.spin()
    def add_banner(self):
        tmp = Banner(len(self.banners))
        for strat in self.strategies.values():
            strat.add_banner(tmp)
        self.banners.append(tmp)

sim = Simulation()
fig, (ax1, ax2) = plt.subplots(1, 2)

if 'sim' not in st.session_state:
    st.session_state.sim = Simulation()


if st.button("Добавить баннер"):
    st.session_state.sim.add_banner()
    print(len(st.session_state.sim.banners))
    
if st.button("Spin"):
    st.session_state.sim.make_simulation(1)
for ban in st.session_state.sim.banners:
        ax1.axvline(x=ban.conversion_prob, color=ban.color, linestyle='--', linewidth=2)
for i in range(len(st.session_state.sim.strategies['Greedy'].reward)):
    print(st.session_state.sim.strategies['Greedy'].reward)
    ax2.axvline(x=st.session_state.sim.strategies['Greedy'].reward[i], color=st.session_state.sim.strategies['Greedy'].banners[i].color, linestyle='--', linewidth=2)
st.pyplot(fig)