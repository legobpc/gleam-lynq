<template>
    <div class="max-w-xl mx-auto mt-10 p-4 border rounded shadow">
      <h2 class="text-2xl font-bold mb-4">Domain Checker</h2>
      <form @submit.prevent="checkDomain">
        <input
          v-model="domain"
          type="text"
          placeholder="Enter a domain (e.g., google.com)"
          class="w-full p-2 border rounded mb-4"
          required
        />
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          {{ loading ? 'Checking...' : 'Check Domain' }}
        </button>
      </form>
  
      <div v-if="error" class="mt-4 text-red-500">
        {{ error }}
      </div>
  
      <div v-if="result" class="mt-6 bg-gray-100 p-4 rounded">
        <h3 class="text-lg font-semibold mb-2">Result:</h3>
        <p><strong>Fixed Domain:</strong> {{ result.fixed_domain }}</p>
        <p><strong>DNS Status:</strong> {{ result.dns_status }}</p>
        <p><strong>HTTP Status:</strong> {{ result.http_status ?? 'N/A' }}</p>
        <p><strong>Is Live:</strong> {{ result.is_live ? 'Yes ✅' : 'No ❌' }}</p>
        <p><strong>Final URL:</strong> {{ result.final_url ?? 'N/A' }}</p>
        <p><strong>Redirected:</strong> {{ result.redirected === null ? 'N/A' : result.redirected ? 'Yes' : 'No' }}</p>
        <p><strong>Response Time:</strong> {{ result.response_time ?? 'N/A' }} sec</p>
        <p><strong>Message:</strong> {{ result.message }}</p>
  
        <div v-if="result.redirect_chain.length > 0" class="mt-4">
          <h4 class="font-semibold">Redirect Chain:</h4>
          <ul class="list-disc list-inside">
            <li v-for="(url, index) in result.redirect_chain" :key="index">{{ url }}</li>
          </ul>
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
  