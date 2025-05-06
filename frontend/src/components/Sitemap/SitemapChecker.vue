<template>
  <div class="w-full">
    <!-- Form -->
    <form @submit.prevent="checkSitemap" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-blue-400 mb-2">
          Enter Domain
        </label>
        <input
          v-model="domain"
          type="text"
          placeholder="e.g., google.com"
          class="w-full p-4 border-2 border-gray-700 rounded-md bg-[#1e1e1e] text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-200 transition"
          required
        />
      </div>
      <button
        type="submit"
        :disabled="loading"
        class="w-auto px-4 py-3 bg-blue-400 text-white font-semibold rounded-md hover:bg-blue-500 transition disabled:opacity-50"
      >
        {{ loading ? 'Checking...' : 'Check Sitemap' }}
      </button>
    </form>

    <!-- Error -->
    <div v-if="error" class="mt-6 text-red-400 text-lg font-medium border-t-2 border-red-400 pt-4">
      {{ error }}
    </div>

    <!-- Result -->
    <div v-if="result" class="mt-10 w-full p-6 bg-[#1e1e1e] rounded-lg border-4 border-blue-400 shadow-lg shadow-blue-500/30 transition-all duration-300">
      <h3 class="text-xl font-semibold mb-4 text-blue-300 border-b-2 border-blue-300 pb-2">
        Sitemap Overview
      </h3>
      <div class="space-y-2 text-gray-200">
        <p><span class="font-medium text-blue-300">Sitemap URL:</span> {{ result.sitemap_url }}</p>
        <p><span class="font-medium text-blue-300">Sitemap Status:</span> {{ result.sitemap_status }}</p>
        <p><span class="font-medium text-blue-300">HTTP Status:</span> {{ result.http_status ?? 'N/A' }}</p>
        <p><span class="font-medium text-blue-300">Message:</span> {{ result.message }}</p>
      </div>

      <!-- Immediate URLs -->
      <div v-if="result.urls.length" class="mt-6 overflow-auto max-h-[600px]">
        <h4 class="font-semibold text-blue-300 mb-2">Extracted URLs ({{ result.urls.length }})</h4>
        <table class="min-w-full bg-[#2c2c2c] text-gray-200 text-sm rounded-lg overflow-hidden">
          <thead class="bg-[#3c3c3c] text-left">
            <tr>
              <th class="px-4 py-2">#</th>
              <th class="px-4 py-2">URL</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(url, index) in result.urls" :key="index"
              class="border-b border-gray-700 hover:bg-[#3a3a3a]">
              <td class="px-4 py-2">{{ index + 1 }}</td>
              <td class="px-4 py-2 break-all text-blue-400 hover:underline">{{ url }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Sitemap Files List -->
      <div v-if="result.sitemap_files.length" class="mt-6 overflow-auto max-h-[600px]">
        <h4 class="font-semibold text-blue-300 mb-2">Sitemap Files ({{ result.sitemap_files.length }})</h4>
        <table class="min-w-full bg-[#2c2c2c] text-gray-200 text-sm rounded-lg overflow-hidden">
          <thead class="bg-[#3c3c3c] text-left">
            <tr>
              <th class="px-4 py-2">#</th>
              <th class="px-4 py-2">Sitemap URL</th>
              <th class="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(url, index) in result.sitemap_files" :key="index"
              class="border-b border-gray-700 hover:bg-[#3a3a3a]">
              <td class="px-4 py-2">{{ index + 1 }}</td>
              <td class="px-4 py-2 break-all text-blue-400 hover:underline">{{ url }}</td>
              <td class="px-4 py-2">
                <button
                  class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-md disabled:opacity-50"
                  @click="fetchUrls(url)"
                  :disabled="loadingDetails[url]"
                >
                  {{ loadingDetails[url] ? 'Loading...' : 'View URLs' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Loaded URLs from Sub-Sitemaps -->
      <div v-if="urlsPerSitemap.length" v-for="(urls, sitemapUrl) in urlsPerSitemap" :key="sitemapUrl" class="mt-6">
        <h4 class="font-semibold text-blue-300 mb-2 break-all">
          URLs from: {{ sitemapUrl }} ({{ urls.length }})
        </h4>
        <table class="min-w-full bg-[#2c2c2c] text-gray-200 text-sm rounded-lg overflow-hidden">
          <thead class="bg-[#3c3c3c] text-left">
            <tr>
              <th class="px-4 py-2">#</th>
              <th class="px-4 py-2">URL</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(url, index) in urls" :key="index"
              class="border-b border-gray-700 hover:bg-[#3a3a3a]">
              <td class="px-4 py-2">{{ index + 1 }}</td>
              <td class="px-4 py-2 break-all text-blue-400 hover:underline">{{ url }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import apiClient from '@/plugins/axios'

const domain = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)

const loadingDetails = reactive({})
const urlsPerSitemap = reactive({})

const checkSitemap = async () => {
  result.value = null
  error.value = null
  loading.value = true
  urlsPerSitemap.value = {}

  try {
    const response = await apiClient.post('/sitemap/check-sitemap', {
      domain: domain.value
    })
    result.value = response.data
  } catch (err) {
    if (err.response?.data) {
      error.value = err.response.data.error || err.response.data.detail || 'Unknown error'
    } else {
      error.value = 'Connection error'
    }
  } finally {
    loading.value = false
  }
}

const fetchUrls = async (sitemapUrl) => {
  if (urlsPerSitemap[sitemapUrl]) return
  loadingDetails[sitemapUrl] = true

  try {
    const response = await apiClient.post('/sitemap/fetch-sitemap-urls', {
      sitemap_url: sitemapUrl
    })
    urlsPerSitemap[sitemapUrl] = response.data.urls
  } catch (err) {
    console.error('Failed to fetch URLs for', sitemapUrl)
  } finally {
    loadingDetails[sitemapUrl] = false
  }
}
</script>

<style scoped>
</style>
