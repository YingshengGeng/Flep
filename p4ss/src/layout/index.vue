<template>
  <div
    class="flex h-dvh w-dvw flex-col items-stretch bg-[#EEF1FA] text-sm text-gray-800"
  >
    <!-- 1.顶部状态栏 -->
    <header
      class="z-20 flex h-14 shrink-0 grow-0 items-center gap-2 border-b border-gray-300 bg-white px-6 shadow"
    >
      <logo-svg
        class="shrink-0 grow-0 cursor-pointer"
        @click="$router.replace('/')"
      />
      <p
        class="flex-auto cursor-pointer select-none font-bold text-black"
        @click="$router.replace('/')"
      >
        P4 仿真系统
      </p>
      <div
        class="flex h-8 shrink-0 grow-0 flex-nowrap items-center gap-2 rounded-2xl bg-[#EEF1FA] px-4"
      >
        <time-svg class="sshrink-0 grow-0" />
        <p>{{ dateToString(Date.now(), 'YYYY-MM-DD HH:mm') }}</p>
      </div>
      <div
        class="flex h-full shrink-0 grow-0 cursor-pointer flex-nowrap items-center gap-2 px-4 transition"
      >
        <avatar-svg class="shrink-0 grow-0" />
        <p>张教授</p>
        <p>▼</p>
      </div>
    </header>

    <!-- 2.底部内容 -->
    <section
      class="flex flex-auto flex-row flex-nowrap items-stretch overflow-hidden"
    >
      <!-- 左侧导航栏 -->
      <aside
        class="z-10 flex w-52 shrink-0 grow-0 flex-col flex-nowrap bg-white shadow"
      >
        <ul class="px-3 py-5">
          <li
            class="flex h-10 cursor-pointer items-center gap-2 rounded-lg px-3 transition"
            :class="
              $route.path === '/reliable-communication'
                ? 'bg-[#EEF5FF] text-[#0059E5]'
                : 'hover:bg-[#EEF5FF]'
            "
            @click="$router.push('/reliable-communication')"
          >
            <communication-svg class="shrink-0 grow-0" />
            <p>可靠通信网络调度</p>
          </li>
          <li
            class="mt-3 flex h-10 cursor-pointer items-center gap-2 rounded-lg px-3 transition"
            :class="
              $route.path === '/network-node'
                ? 'bg-[#EEF5FF] text-[#0059E5]'
                : 'hover:bg-[#EEF5FF]'
            "
            @click="$router.push('/network-node')"
          >
            <network-svg class="shrink-0 grow-0" />
            <p>网络节点信息</p>
          </li>
          <li
            class="mt-3 flex h-10 cursor-pointer items-center gap-2 rounded-lg px-3 transition"
            :class="
              $route.path === '/system-api'
                ? 'bg-[#EEF5FF] text-[#0059E5]'
                : 'hover:bg-[#EEF5FF]'
            "
            @click="$router.push('/system-api')"
          >
            <system-svg class="shrink-0 grow-0" />
            <p>系统调度接口</p>
          </li>
        </ul>
      </aside>

      <!-- 右侧路由 -->
      <main id="main" class="flex-auto overflow-y-auto">
        <router-view v-slot="{ Component, route }">
          <transition name="router" mode="out-in">
            <keep-alive :include="[]">
              <component :is="Component" :key="route.fullPath" />
            </keep-alive>
          </transition>
        </router-view>
      </main>
    </section>
  </div>
  <el-backtop target="#main" />
</template>

<script setup lang="ts">
import { dateToString } from '@/utils/date'
import LogoSvg from '@/assets/svg/logo.svg'
import TimeSvg from '@/assets/svg/time.svg'
import AvatarSvg from '@/assets/svg/avatar.svg'
import CommunicationSvg from '@/assets/svg/communication.svg'
import NetworkSvg from '@/assets/svg/network.svg'
import SystemSvg from '@/assets/svg/system.svg'
</script>
