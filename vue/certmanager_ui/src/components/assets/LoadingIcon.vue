<template>
    <div class="vista-loader"></div>
</template>

<script>
    export default {
        name: 'CertificateSubj',
        components: {

        },
        data() {
            return {
   
            }
        },
        methods: {

        }
    }
</script>

<style scoped>

    .vista-loader {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      position: relative;
      animation: spin 1.2s linear infinite;

      /* glowing pearl gradient */
      background: conic-gradient(
        rgba(0, 200, 255, 0) 0deg,
        rgba(0, 200, 255, 0.8) 60deg,
        rgba(0, 200, 255, 1) 90deg,
        rgba(0, 200, 255, 0.8) 120deg,
        rgba(0, 200, 255, 0) 180deg,
        rgba(0, 200, 255, 0) 360deg
      );

      /* hollow center */
      -webkit-mask: radial-gradient(circle, transparent 40%, black 71%);
      mask: radial-gradient(circle, transparent 50%, black 71%);
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }


</style>