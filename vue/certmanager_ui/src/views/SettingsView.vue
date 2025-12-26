<template>
  <div style="width: 80vw; height: 80vh; margin-left: auto; margin-right: auto; margin-top: 30px;">
  <h2 style="text-align: left;">SETTINGS</h2>
  <div class="glass_container" style="height: 100%; padding: 10px;">
    <div class="glass_container_divider" style="width: 20vw; float: left; text-align: left; height: calc(100% - 15px);">
      <button :class="this.selected_setting=='user_profile' ? 'glass-button-selected': 'glass-button'" v-on:click="this.selected_setting = 'user_profile'"><img class="icon" src="/icons/administrator.png">&nbsp; User Profile</button>
      <br>
      <button :class="this.selected_setting=='manage_users' ? 'glass-button-selected': 'glass-button'" v-on:click="this.selected_setting = 'manage_users'"><img class="icon" src="/icons/group.png">&nbsp;&nbsp;Manage Other Users</button>
      <br>
      <button :class="this.selected_setting=='system_logs' ? 'glass-button-selected': 'glass-button'" v-on:click="this.selected_setting = 'system_logs'"><img class="icon" src="/icons/contract.png">&nbsp;&nbsp;System Logs</button>
      <button :class="this.selected_setting=='certificiate_wizzard' ? 'glass-button-selected': 'glass-button'" v-on:click="$router.push({ path: '/createcert' })"><img class="icon" src="/icons/wizard.png">&nbsp;&nbsp;Certificate Wizard</button>

    </div>

    <div class="glass_container_divider" style="width: 59vw; float: right; text-align: left; height: calc(100% - 15px)">
      <AboutMe v-if="this.selected_setting == 'user_profile'"></AboutMe>
      <ManageUsers v-if="this.selected_setting == 'manage_users'"></ManageUsers>
      <SystemLogs v-if="this.selected_setting == 'system_logs'"></SystemLogs>
    </div>
  </div>
  </div>
</template>

<script>
import AboutMe from '@/components/assets/AboutMe.vue';
import ManageUsers from '@/components/assets/ManageUsers.vue';
import SystemLogs from '@/components/assets/SystemLogs.vue';

// @ is an alias to /src

export default {
  name: 'SettingsView',
  components: {
    AboutMe, ManageUsers, SystemLogs
  },
  data () {
    return {
      selected_setting: "user_profile"
    }
  }
}
</script>

<style scoped>

  h2 {
    margin: 1px;
    text-transform: uppercase;
    font-weight: 400;
  }

  div.glass_container {
    overflow: auto;
    margin: auto;
    margin-top: 10px;
    border-radius: 10px;
    width: 100%;

  /* Thicker, smoother liquid glass base */
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.25),
    rgba(180, 220, 255, 0.08),
    rgba(255, 182, 193, 0.05)
  );
  background-size: 200% 200%;
  animation: liquidShift 12s ease infinite;

  backdrop-filter: blur(20px) saturate(200%);
  -webkit-backdrop-filter: blur(20px) saturate(200%);

  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow:
    inset 0 0 10px rgba(255, 255, 255, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.25);;

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;

  }



  /* Optional: custom scrollbar for WebKit browsers */
  div.table_container::-webkit-scrollbar {
    width: 6px;
  }

  div.table_container::-webkit-scrollbar-track {
    background: transparent;
  }

  div.table_container::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.4);
    border-radius: 20px;
  }


  div.glass_container_divider {
    overflow: auto;
    margin: auto;
    margin-top: 10px;
    margin-bottom: 10px;
    border-radius: 10px;

    /* Apple Glassmorphism base */
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Subtle borders */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
  }


   .glass-button {
    padding: 15px 25px;
    border-radius: 5px;
    font-size: 0.9em;
    font-weight: 500;
    margin: 5px;
    width: calc(100% - 10px);
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: left;


  background: linear-gradient(
    to bottom right,
    rgba(255, 255, 255, 0.35),
    rgba(255, 255, 255, 0.05)
  );
  backdrop-filter: blur(20px) saturate(200%);
  -webkit-backdrop-filter: blur(20px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow:
    inset 0 0 6px rgba(255, 255, 255, 0.3),
    0 4px 25px rgba(0, 0, 0, 0.25);

    /* Smooth transition */
    transition: all 0.3s ease;
    vertical-align: middle;
  }



   .glass-button-selected {
    padding: 15px 25px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: 500;
    margin: 5px;
    width: calc(100% - 10px);
    color: #fff;
    /* White text works best on glass */
    cursor: pointer;
    text-align: left;

  background: linear-gradient(
    to bottom right,
    rgba(50, 50, 50, 0.35),
    rgba(30, 30, 30, 0.15)
  );
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow:
    inset 0 0 10px rgba(255, 255, 255, 0.4),
    0 6px 28px rgba(0, 0, 0, 0.3);

    /* Smooth transition */
    transition: all 0.3s ease;
    vertical-align: top;
  }

  /* Hover effect */
  .glass-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
  box-shadow:
    0 8px 28px rgba(0, 0, 0, 0.3),
    inset 0 0 10px rgba(255, 255, 255, 0.4);
  }


    img.icon{
    height: 25px;
    vertical-align: middle;
  }


</style>
