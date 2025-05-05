<script setup>
import { ref } from 'vue'
import DomainChecker from './components/Domain/DomainChecker.vue'

const tabs = [
  { id: 'domain', label: 'Domain Checker' },
  { id: 'other1', label: 'Page Analyzer' },
  { id: 'other2', label: 'Google Position Tracker' },
]

const activeTab = ref('domain')
</script>

<template>
  <div class="min-h-screen bg-[#212121] text-gray-100">
    <!-- Sidebar (fixed position + fixed width) -->
    <aside
      class="fixed top-0 left-0 h-full w-[220px] border-r-2 border-gray-700 flex flex-col p-4 bg-[#212121] z-10"
    >
      <h2 class="text-xl font-bold text-green-400 mb-6">Gleam Lynq</h2>
      <nav class="flex flex-col space-y-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'text-left px-4 py-3 rounded-md font-medium transition border-l-4',
            activeTab === tab.id
              ? 'bg-[#2a2a2a] text-green-400 border-green-400'
              : 'hover:bg-[#2a2a2a] text-gray-300 border-transparent'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="ml-[220px] p-8">
      <div v-if="activeTab === 'domain'">
        <DomainChecker />
      </div>

      <div v-else-if="activeTab === 'other1'">
        <p>Тут буде ще один інструмент 👌</p>
      </div>

      <div v-else-if="activeTab === 'other2'">
        <p>Тут ще один майбутній блок 🚀</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
</style>
