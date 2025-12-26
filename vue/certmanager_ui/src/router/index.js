import {
  createRouter,
  createWebHistory
} from 'vue-router'
import LogonWindow from '@/LogonWindow.vue'
import HelloWorld from '@/components/HelloWorld.vue'
import TreeView from '@/views/TreeView.vue'
import CreateCert from '@/components/CreateCert.vue'
import SettingsView from '@/views/SettingsView.vue'
import ApiDocs from '@/views/ApiDocs.vue'

const routes = [{
    path: '/',
    name: 'home',
    component: HelloWorld
  },
  {
    path: '/login',
    name: 'login',
    meta: {
      hideNavbar: true
    },
    component: LogonWindow
  },

  {
    path: '/tree',
    name: 'tree',
    component: TreeView
  },
  {
    path: '/createcert',
    name: 'createcert',
    component: CreateCert
  },
  {
    path:'/settings',
    name:'settings',
    component: SettingsView
  },
  {
    path:'/apidocs',
    name:'apidocs',
    component: ApiDocs
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router