from os import X_OK
from tracemalloc import start
import numpy as np
from regex import T
import streamlit as st
import matplotlib.pyplot as plt
from scipy.stats import beta, norm
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
        self.banners = []
        self.reward = []
        self.spin_count = []

    # @classmethod
    # @abstractmethod
    def spin(self):
        pass

    # @classmethod
    # @abstractmethod
    def add_banner(self, banner):
        self.banners.append(banner)
        self.reward.append(0.0)
        self.spin_count.append(0)

    def calculate_reward(self, chosen_arm):
        n = self.spin_count[chosen_arm] + 1
        self.spin_count[chosen_arm] = n
        val = self.reward[chosen_arm]
        curr_reward = self.banners[chosen_arm].click()
        self.reward[chosen_arm] = ((n - 1)/n) * val + (curr_reward / n)
        return curr_reward

class ThomsonSampling(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.alpha_bettas = []
        # self.eps = eps
    def spin(self):
        mx = -1
        save_i = 0
        for i in range(len(self.banners)):
            tmp_betta = np.random.beta(self.alpha_bettas[i][0], self.alpha_bettas[i][1])
            if tmp_betta > mx:
                mx = tmp_betta
                save_i = i
        self.calculate_reward(save_i)
        

    def add_banner(self, banner) -> None:
        super().add_banner(banner)
        self.alpha_bettas.append([1, 1])
    
    def calculate_reward(self, chosen_arm):
        res = super().calculate_reward(chosen_arm)
        if res == 1:
            self.alpha_bettas[chosen_arm][0] += 1
        else:
            self.alpha_bettas[chosen_arm][1] += 1


class UCB(Strategy):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.M2 = []

    def add_banner(self, banner):
        super().add_banner(banner)
        self.M2.append(0)
        self.calculate_reward(len(self.banners) - 1)
        self.n += 1
    
    def spin(self):
        mx = -1
        save_i = 0
        for i in range(len(self.spin_count)):
            tmp_rew = (self.reward[i]/self.spin_count[i])
            tmp_spins = np.sqrt((2 * np.log(self.n))/ self.spin_count[i])
            tmp_mx = tmp_rew + tmp_spins
            # print(tmp_mx, tmp_rew, tmp_spins)
            if tmp_mx > mx:
                mx = tmp_mx
                save_i = i
        self.calculate_reward(save_i)
        
    def calculate_reward(self, chosen_arm):
        self.n += 1
        n = self.spin_count[chosen_arm] + 1
        self.spin_count[chosen_arm] = n
        val = self.reward[chosen_arm]
        tmp_res = self.banners[chosen_arm].click()
        self.reward[chosen_arm] = ((n - 1)/n) * val + (tmp_res / n)
        self.M2[chosen_arm] = self.M2[chosen_arm] + (tmp_res - val) * (tmp_res - self.reward[chosen_arm])
    
    def variance(self, chosen_arm):
        return self.M2[chosen_arm] / self.spin_count[chosen_arm] if self.spin_count[chosen_arm] > 1 else 0.0




class EpsilonGreedy(Strategy):
    def __init__(self, eps):
        super().__init__()
        self.eps = eps
        self.M2 = []

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


    def add_banner(self, banner):
        super().add_banner(banner)
        self.M2.append(0)
    

    def calculate_reward(self, chosen_arm):
        n = self.spin_count[chosen_arm] + 1
        self.spin_count[chosen_arm] = n
        val = self.reward[chosen_arm]
        tmp_res = self.banners[chosen_arm].click()
        self.reward[chosen_arm] = ((n - 1)/n) * val + (tmp_res / n)
        self.M2[chosen_arm] = self.M2[chosen_arm] + (tmp_res - val) * (tmp_res - self.reward[chosen_arm])

    def variance(self, chosen_arm):
        return self.M2[chosen_arm] / self.spin_count[chosen_arm] if self.spin_count[chosen_arm] > 1 else 0.0




class Simulation:
    def __init__(self) -> None:
        self.banners =  []
        self.strategies = {}
        self.strategies['Greedy'] = EpsilonGreedy(0.9)
        self.strategies['UCB'] = UCB()
        self.strategies['Thompson'] = ThomsonSampling()


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
fig, ax = plt.subplots(len(sim.strategies) + 1, 1, figsize=(10,10))

if 'sim' not in st.session_state:
    st.session_state.sim = Simulation()


if st.button("Добавить баннер"):
    st.session_state.sim.add_banner()
    print(len(st.session_state.sim.banners))
    
value = int(st.number_input("Введите количество нажатий:", 
                       min_value=0.0, 
                       value=100.0, 
                       format="%.0f",
                       step=10.0))
st.metric("Количество кликов", value)
x_line = np.linspace(0, 1, 100)    
if st.button("Spin"):
    st.session_state.sim.make_simulation(value)
for ban in st.session_state.sim.banners:
        ax[0].axvline(x=ban.conversion_prob, color=ban.color, linestyle='--', linewidth=2)
        st.markdown(f'<div style="color: rgb({ban.color[0] * 255}, {ban.color[1] * 255}, {ban.color[2] * 255}); font-size: 1.5em;"> Реальная вероятность: Вероятность: {ban.conversion_prob}</div>', unsafe_allow_html=True)
for j, (key, strat) in enumerate(st.session_state.sim.strategies.items()):
    print(strat)
    for i in range(len(strat.reward)):
        # print(strat.reward)
        ax[j + 1].axvline(x=strat.reward[i], color=strat.banners[i].color, linestyle='--', linewidth=2)
        if key == 'Greedy':
            dist = norm(strat.reward[i], np.sqrt(strat.variance(i)))
            rasp = dist.pdf(x_line)
            ax[j+1].plot(x_line, rasp, color=strat.banners[i].color, linewidth=2)#, label=f'Beta(α={self.alpha}, β={beta_param})')
        elif key == 'UCB':
            dist = norm(strat.reward[i], np.sqrt(strat.variance(i)))
            rasp = dist.pdf(x_line)
            ax[j+1].plot(x_line, rasp, color=strat.banners[i].color, linewidth=2)#, label=f'Beta(α={self.alpha}, β={beta_param})')
        elif key == 'Thompson':
            rasp = beta.pdf(x_line, strat.alpha_bettas[i][0], strat.alpha_bettas[i][1])
            ax[j+1].plot(x_line, rasp, color=strat.banners[i].color, linewidth=2)#, label=f'Beta(α={self.alpha}, β={beta_param})')
        st.markdown(f'<div style="color: rgb({strat.banners[i].color[0] * 255}, {strat.banners[i].color[1] * 255}, {strat.banners[i].color[2] * 255}); font-size: 1.5em;"> {key}: Вероятность: {strat.reward[i]}, Прокруток: {strat.spin_count[i]}</div>', 
            unsafe_allow_html=True)
st.pyplot(fig)



# Вывод введенного значения
# st.write("Вы ввели:", value)
