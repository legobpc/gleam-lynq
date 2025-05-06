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

    <div
      v-if="error"
      class="mt-6 text-red-400 text-lg font-medium border-t-2 border-red-400 pt-4"
    >
      {{ error }}
    </div>

    <div
      v-if="result"
      class="mt-10 w-full p-6 bg-[#1e1e1e] rounded-lg border-4 border-orange-400 shadow-lg shadow-orange-500/30 transition-all duration-300 space-y-4"
    >
      <h3
        class="text-xl font-semibold mb-4 text-orange-300 border-b-2 border-orange-300 pb-2 flex items-center gap-2"
      >
        <Code2 class="w-5 h-5" /> Result
      </h3>
      <div class="space-y-2 text-gray-200 text-sm">
        <div class="flex items-center gap-2">
          <Globe class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">URL:</span>
            {{ result.url }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Server class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">HTTP Status:</span>
            {{ result.http_status ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Repeat class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Redirected:</span>
            {{ result.redirected ? 'Yes' : 'No' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Link class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Final URL:</span>
            {{ result.final_url ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Heading class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Title:</span>
            {{ result.title ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <AlignLeft class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Description:</span>
            {{ result.description ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <CheckCircle class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Canonical Matches:</span>
            {{ result.canonical_matches ? 'Yes' : 'No' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Link2 class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Canonical:</span>
            {{ result.canonical ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Hash class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">H1:</span>
            {{ result.h1 ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <FileText class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Content Type:</span>
            {{ result.content_type ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Package class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Content Length:</span>
            {{ result.content_length ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <EyeOff class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Robots Meta:</span>
            {{ result.robots_meta ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Bot class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">X-Robots-Tag:</span>
            {{ result.x_robots_tag ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Languages class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Lang:</span>
            {{ result.lang ?? 'N/A' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Image class="w-4 h-4 text-orange-300" />
          <p>
            <span class="font-medium text-orange-300">Favicon:</span>
            {{ result.favicon_url ?? 'N/A' }}
          </p>
        </div>

        <!-- Accordion Blocks -->
        <DisclosureBlock
          v-if="result.open_graph && Object.keys(result.open_graph).length"
          title="Open Graph"
          :icon="Globe"
        >
          <ul class="list-disc list-inside space-y-1">
            <li v-for="(val, key) in result.open_graph" :key="key">
              <span class="font-medium text-orange-300">{{ key }}:</span>
              {{ val }}
            </li>
          </ul>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.twitter_meta && Object.keys(result.twitter_meta).length"
          title="Twitter Meta"
          :icon="Twitter"
        >
          <ul class="list-disc list-inside space-y-1">
            <li v-for="(val, key) in result.twitter_meta" :key="key">
              <span class="font-medium text-orange-300">{{ key }}:</span>
              {{ val }}
            </li>
          </ul>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.all_h1 && result.all_h1.length"
          title="All H1"
          :icon="Hash"
        >
          <ul class="list-disc list-inside space-y-1">
            <li v-for="(h1, idx) in result.all_h1" :key="idx">
              {{ h1 }}
            </li>
          </ul>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.headings && result.headings.length"
          title="Headings"
          :icon="ListOrdered"
        >
          <ul class="list-disc list-inside space-y-1">
            <li v-for="(heading, idx) in result.headings" :key="idx">
              <span class="font-medium text-orange-300">{{ heading.tag }}:</span>
              {{ heading.text }}
            </li>
          </ul>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.alternate_hreflang && result.alternate_hreflang.length"
          title="Alternate Hreflangs"
          :icon="Languages"
        >
          <ul class="list-disc list-inside space-y-1">
            <li v-for="(alt, idx) in result.alternate_hreflang" :key="idx">
              <span class="font-medium text-orange-300">{{ alt.hreflang }}:</span>
              {{ alt.href }}
            </li>
          </ul>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.schema_json_ld"
          title="JSON-LD Schema"
          :icon="FileJson"
        >
          <pre
            class="bg-[#2c2c2c] p-2 rounded text-xs overflow-x-auto"
          >{{ result.schema_json_ld }}</pre>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.headers && Object.keys(result.headers).length"
          title="Headers"
          :icon="ServerCog"
        >
          <ul class="list-disc list-inside space-y-1">
            <li v-for="(val, key) in result.headers" :key="key">
              <span class="font-medium text-orange-300">{{ key }}:</span>
              {{ val }}
            </li>
          </ul>
        </DisclosureBlock>

        <DisclosureBlock
          v-if="result.seo_checks && Object.keys(result.seo_checks).length"
          title="SEO Checks"
          :icon="CheckCircle"
        >
          <ul class="space-y-2">
            <li
              v-for="(check, key) in result.seo_checks"
              :key="key"
              class="bg-[#2c2c2c] rounded p-3 flex flex-col gap-1 border-l-4"
              :class="check.passed === 'True' ? 'border-green-400' : 'border-red-400'"
            >
              <div class="flex justify-between items-center">
                <span class="font-medium text-orange-300 capitalize">{{ key.replace(/_/g, ' ') }}</span>
                <span
                  class="text-sm font-semibold"
                  :class="check.passed === 'True' ? 'text-green-400' : 'text-red-400'"
                >
                  {{ check.passed === 'True' ? '✅ Passed' : '❌ Failed' }}
                </span>
              </div>
              <p class="text-xs text-gray-400 leading-snug">
                {{ check.message }}
              </p>
            </li>
          </ul>
        </DisclosureBlock>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import apiClient from '@/plugins/axios'
import {
  Globe,
  Code2,
  Server,
  Repeat,
  Link,
  Heading,
  AlignLeft,
  Twitter,
  ListOrdered,
  Languages,
  FileJson,
  ServerCog,
  Hash,
  FileText,
  Package,
  EyeOff,
  Bot,
  Image,
  Link2,
  CheckCircle,
} from 'lucide-vue-next'

import DisclosureBlock from '@/components/Shared/DisclosureBlock.vue' // додай це

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
      url: url.value,
    })

    result.value = response.data
  } catch (err) {
    if (err.response?.data) {
      error.value =
        err.response.data.error ||
        err.response.data.detail ||
        'Unknown error'
    } else {
      error.value = 'Connection error'
    }
  } finally {
    loading.value = false
  }
}
</script>

<!-- DisclosureBlock Component -->
<script>
import { defineComponent, h } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { ChevronDown } from 'lucide-vue-next'

export default defineComponent({
  name: 'DisclosureBlock',
  props: {
    title: String,
    icon: Object, // прямо передаємо компонент іконки
  },
  setup(props, { slots }) {
    return () =>
      h(Disclosure, {}, {
        default: ({ open }) => [
          h(DisclosureButton, {
            class:
              'flex justify-between w-full px-4 py-2 text-sm font-medium text-left text-orange-300 bg-[#2c2c2c] rounded-lg hover:bg-orange-500/20 transition'
          }, [
            h('div', { class: 'flex items-center gap-2' }, [
              h(props.icon, { class: 'w-4 h-4' }),
              props.title,
            ]),
            h(ChevronDown, {
              class: [
                'w-4 h-4 transition-transform duration-300',
                open ? 'rotate-180' : ''
              ],
            }),
          ]),
          h(DisclosurePanel, { class: 'px-4 pt-4 pb-2 text-sm text-gray-200' }, slots.default?.())
        ],
      })
  },
})
</script>
