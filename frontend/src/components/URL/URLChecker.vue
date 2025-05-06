<template>
    <div class="w-full">
      <form @submit.prevent="checkUrl" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-orange-400 mb-2">
            Enter URL
          </label>
          <input
            v-model="url"
            type="text"
            placeholder="e.g., https://google.com/page"
            class="w-full p-4 border-2 border-gray-700 rounded-md bg-[#1e1e1e] text-gray-100 placeholder-gray-500 focus:outline-none focus:border-orange-400 focus:ring-4 focus:ring-orange-200 transition"
            required
          />
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="w-auto px-4 py-3 bg-orange-400 text-white font-semibold rounded-md hover:bg-orange-500 transition disabled:opacity-50"
        >
          {{ loading ? 'Checking...' : 'Check URL' }}
        </button>
      </form>
  
      <div v-if="error" class="mt-6 text-red-400 text-lg font-medium border-t-2 border-red-400 pt-4">
        {{ error }}
      </div>
  
      <div v-if="result" class="mt-8 p-6 bg-[#1e1e1e] rounded-lg border-2 border-orange-400 shadow">
        <h3 class="text-xl font-semibold mb-4 text-orange-300 border-b-2 border-orange-300 pb-2">
          Result
        </h3>
        <div class="space-y-2 text-gray-200 text-sm">
          <p><span class="font-medium text-orange-300">URL:</span> {{ result.url }}</p>
          <p><span class="font-medium text-orange-300">HTTP Status:</span> {{ result.http_status ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Redirected:</span> {{ result.redirected ? 'Yes' : 'No' }}</p>
          <p><span class="font-medium text-orange-300">Final URL:</span> {{ result.final_url ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Title:</span> {{ result.title ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Description:</span> {{ result.description ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Canonical:</span> {{ result.canonical ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">H1:</span> {{ result.h1 ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Content Type:</span> {{ result.content_type ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Content Length:</span> {{ result.content_length ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Robots Meta:</span> {{ result.robots_meta ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">X-Robots-Tag:</span> {{ result.x_robots_tag ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Lang:</span> {{ result.lang ?? 'N/A' }}</p>
          <p><span class="font-medium text-orange-300">Favicon:</span> {{ result.favicon_url ?? 'N/A' }}</p>
  
          <div v-if="result.open_graph && Object.keys(result.open_graph).length" class="mt-4">
            <h4 class="font-semibold text-orange-300 mb-2">Open Graph</h4>
            <ul class="list-disc list-inside space-y-1">
              <li v-for="(val, key) in result.open_graph" :key="key">
                <span class="font-medium text-orange-300">{{ key }}:</span> {{ val }}
              </li>
            </ul>
          </div>
  
          <div v-if="result.twitter_meta && Object.keys(result.twitter_meta).length" class="mt-4">
            <h4 class="font-semibold text-orange-300 mb-2">Twitter Meta</h4>
            <ul class="list-disc list-inside space-y-1">
              <li v-for="(val, key) in result.twitter_meta" :key="key">
                <span class="font-medium text-orange-300">{{ key }}:</span> {{ val }}
              </li>
            </ul>
          </div>
  
          <div v-if="result.headings && result.headings.length" class="mt-4">
            <h4 class="font-semibold text-orange-300 mb-2">Headings</h4>
            <ul class="list-disc list-inside space-y-1">
              <li v-for="(heading, idx) in result.headings" :key="idx">
                <span class="font-medium text-orange-300">{{ heading.tag }}:</span> {{ heading.text }}
              </li>
            </ul>
          </div>
  
          <div v-if="result.alternate_hreflang && result.alternate_hreflang.length" class="mt-4">
            <h4 class="font-semibold text-orange-300 mb-2">Alternate Hreflangs</h4>
            <ul class="list-disc list-inside space-y-1">
              <li v-for="(alt, idx) in result.alternate_hreflang" :key="idx">
                <span class="font-medium text-orange-300">{{ alt.hreflang }}:</span> {{ alt.href }}
              </li>
            </ul>
          </div>
  
          <div v-if="result.schema_json_ld" class="mt-4">
            <h4 class="font-semibold text-orange-300 mb-2">JSON-LD Schema</h4>
            <pre class="bg-[#2c2c2c] p-2 rounded text-xs overflow-x-auto">{{ result.schema_json_ld }}</pre>
          </div>
  
          <div v-if="result.headers && Object.keys(result.headers).length" class="mt-4">
            <h4 class="font-semibold text-orange-300 mb-2">Headers</h4>
            <ul class="list-disc list-inside space-y-1">
              <li v-for="(val, key) in result.headers" :key="key">
                <span class="font-medium text-orange-300">{{ key }}:</span> {{ val }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import apiClient from '@/plugins/axios'
  
  const url = ref('')
  const result = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const checkUrl = async () => {
    result.value = null
    error.value = null
    loading.value = true
  
    try {
      const response = await apiClient.post('/url/check-url', {
        url: url.value
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
  </script>
  
  <style scoped>
  </style>
  