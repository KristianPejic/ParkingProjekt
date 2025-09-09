import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './components/Home.vue'
import History from './components/History.vue'
import Stats from './components/Stats.vue'
import Train from './components/Train.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/history', component: History },
  { path: '/stats', component: Stats },
  { path: '/train', component: Train }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
