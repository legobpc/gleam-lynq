<template>
  <div class="w-full">
    <form @submit.prevent="checkDomain" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-green-400 mb-2">
          Enter Domain
        </label>
        <input
          v-model="domain"
          type="text"
          placeholder="e.g., google.com"
          class="w-full p-4 border-2 border-gray-700 rounded-md bg-[#1e1e1e] text-gray-100 placeholder-gray-500 focus:outline-none focus:border-green-400 focus:ring-4 focus:ring-green-200 transition"
          required
        />
      </div>
      <button
        type="submit"
        :disabled="loading"
        class="w-auto px-4 py-3 bg-green-400 text-white font-semibold rounded-md hover:bg-green-500 transition disabled:opacity-50"
      >
        {{ loading ? 'Checking...' : 'Check Domain' }}
      </button>
    </form>

    <div v-if="error" class="mt-6 text-red-400 text-lg font-medium border-t-2 border-red-400 pt-4">
      {{ error }}
    </div>

    <div v-if="result" class="mt-8 p-6 bg-[#1e1e1e] rounded-lg border-2 border-green-400 shadow">
      <h3 class="text-xl font-semibold mb-4 text-green-300 border-b-2 border-green-300 pb-2">
        Result
      </h3>
      <div class="space-y-2 text-gray-200">
        <p><span class="font-medium text-green-300">Fixed Domain:</span> {{ result.fixed_domain }}</p>
        <p><span class="font-medium text-green-300">DNS Status:</span> {{ result.dns_status }}</p>
        <p><span class="font-medium text-green-300">HTTP Status:</span> {{ result.http_status ?? 'N/A' }}</p>
        <p><span class="font-medium text-green-300">Is Live:</span> {{ result.is_live ? 'Yes ✅' : 'No ❌' }}</p>
        <p><span class="font-medium text-green-300">Final URL:</span> {{ result.final_url ?? 'N/A' }}</p>
        <p><span class="font-medium text-green-300">Redirected:</span> {{ result.redirected === null ? 'N/A' : result.redirected ? 'Yes' : 'No' }}</p>
        <p><span class="font-medium text-green-300">Response Time:</span> {{ result.response_time ?? 'N/A' }} sec</p>
        <p><span class="font-medium text-green-300">Message:</span> {{ result.message }}</p>

        <div v-if="result.redirect_chain.length > 0" class="mt-4">
          <h4 class="font-semibold text-green-300 mb-2">Redirect Chain:</h4>
          <ul class="list-decimal list-inside space-y-1 text-gray-300">
            <li v-for="(url, index) in result.redirect_chain" :key="index">{{ url }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import apiClient from '@/plugins/axios'

const domain = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)

const checkDomain = async () => {
  result.value = null
  error.value = null
  loading.value = true

  try {
    const response = await apiClient.post('/domain/check-domain', {
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
</script>

<style scoped>
</style>
