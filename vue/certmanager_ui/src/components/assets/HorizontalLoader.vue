<template>
  <!-- Horizontal loading bar with sweeping pulsing light -->
  <div class="progress-wrap" role="progressbar">
    <div class="progress">
      <div class="shine"></div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'HorizontalLoader',
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
  .progress-wrap {
    width: 100%;
    /* container width */
    margin: 0px auto;
    padding: 0px;
    /* outer padding for soft border */
    background: rgba(38, 103, 224, 0.041);
    border-radius: 0px;
    box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.25);
  }

  .progress {
    position: relative;
    height: 10px;
    /* bar thickness */
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.04));
    border-radius: 0px;
    overflow: hidden;
  }

  /* subtle base fill (optional) */
  .progress::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 0%;
    /* underlying fill — change for partial progress */
    background: linear-gradient(90deg, rgba(130, 180, 255, 0.16), rgba(80, 130, 255, 0.08));
    border-radius: inherit;
    z-index: 1;
  }

  /* the pulsing / shining light */
  .shine {
    position: absolute;
    top: 0px;
    left: 0px;
    width: 100%;
    height: 200%;
    transform: rotate(-12deg);
    background: linear-gradient(90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.55) 45%,
        rgba(255, 255, 255, 0.25) 55%,
        rgba(255, 255, 255, 0) 100%);
    filter: blur(6px);
    opacity: 0.95;
    z-index: 2;
    animation: sweep 2s infinite cubic-bezier(.18, .86, .3, 1);
  }

  /* optional inner soft pulse to make the light breathe */
  .progress::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    box-shadow: 0 0 20px rgba(80, 140, 255, 0.06);
    z-index: 0;
    animation: pulse 1.6s infinite ease-in-out;
  }

  @keyframes sweep {
    0% {
      left: -40%;
      opacity: 0;
      transform: rotate(-12deg) translateX(0) scaleX(0.7);
    }

    10% {
      opacity: 0.6;
    }

    45% {
      left: 60%;
      opacity: 1;
      transform: rotate(-12deg) translateX(0) scaleX(1);
    }

    80% {
      opacity: 0.4;
    }

    100% {
      left: 120%;
      opacity: 0;
      transform: rotate(-12deg) translateX(0) scaleX(0.8);
    }
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 6px rgba(80, 140, 255, 0.02);
    }

    50% {
      box-shadow: 0 0 28px rgba(4, 71, 195, 0.49);
    }

    100% {
      box-shadow: 0 0 6px rgba(80, 140, 255, 0.02);
    }
  }

  /* Responsive: make bar taller on small screens if desired */
  @media (max-width: 480px) {
    .progress {
      height: 10px;
    }
  }
</style>