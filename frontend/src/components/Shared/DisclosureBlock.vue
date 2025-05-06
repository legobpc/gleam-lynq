<template>
    <Disclosure>
      <template #default="{ open }">
        <DisclosureButton
          class="flex justify-between w-full px-4 py-2 text-sm font-medium text-left text-orange-300 bg-[#2c2c2c] rounded-lg hover:bg-orange-500/20 transition"
        >
          <div class="flex items-center gap-2">
            <component :is="icon" class="w-4 h-4" />
            {{ title }}
          </div>
          <ChevronDown
            :class="[
              'w-4 h-4 transition-transform duration-300',
              open ? 'rotate-180' : ''
            ]"
          />
        </DisclosureButton>
        <DisclosurePanel class="px-4 pt-4 pb-2 text-sm text-gray-200">
          <slot />
        </DisclosurePanel>
      </template>
    </Disclosure>
  </template>
  
  <script setup>
  import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
  import { ChevronDown } from 'lucide-vue-next'
  
  defineProps({
    title: String,
    icon: Object,
  })
  </script>
  