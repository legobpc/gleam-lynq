<script setup>
import { ref } from 'vue'
import DomainChecker from './components/Domain/DomainChecker.vue'
import SitemapChecker from './components/Sitemap/SitemapChecker.vue'
import URLChecker from './components/URL/URLChecker.vue'

const tabs = [
  { id: 'domain', label: 'Domain Checker' },
  { id: 'sitemap', label: 'Sitemap Checker' },
  { id: 'url', label: 'URL Checker' },
  { id: 'other2', label: 'Google Position Tracker' },
]

const activeTab = ref('domain')

const getTabClasses = (tab) => {
  const base = 'text-left px-4 py-3 rounded-md font-medium transition border-l-4'

  const isActive = activeTab.value === tab.id

  if (tab.id === 'domain') {
    return isActive
      ? `${base} bg-[#2a2a2a] text-emerald-400 border-emerald-400`
      : `${base} hover:bg-[#2a2a2a] text-gray-300 border-transparent`
  }
  if (tab.id === 'sitemap') {
    return isActive
      ? `${base} bg-[#2a2a2a] text-blue-400 border-blue-400`
      : `${base} hover:bg-[#2a2a2a] text-gray-300 border-transparent`
  }
  if (tab.id === 'url') {
    return isActive
      ? `${base} bg-[#2a2a2a] text-orange-400 border-orange-400`
      : `${base} hover:bg-[#2a2a2a] text-gray-300 border-transparent`
  }
  // Default (neutral)
  return isActive
    ? `${base} bg-[#2a2a2a] text-gray-200 border-gray-400`
    : `${base} hover:bg-[#2a2a2a] text-gray-300 border-transparent`
}
</script>

<template>
  <div class="min-h-screen bg-[#212121] text-gray-100">
    <!-- Sidebar (fixed position + fixed width) -->
    <aside
      class="fixed top-0 left-0 h-full w-[220px] border-r-2 border-gray-700 flex flex-col p-4 bg-[#212121] z-10"
    >
      <h2 class="text-xl font-bold text-white mb-6">Savio</h2>
      <nav class="flex flex-col space-y-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="getTabClasses(tab)"
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

      <div v-else-if="activeTab === 'sitemap'">
        <SitemapChecker />
      </div>

      <div v-else-if="activeTab === 'url'">
        <URLChecker />
      </div>

      <div v-else-if="activeTab === 'other2'">
        <p>Тут ще один майбутній блок 🚀</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
</style>
