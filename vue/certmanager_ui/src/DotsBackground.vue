<template>
  <div class="background-dots">
    <div class="layer layer1"></div>
    <div class="layer layer2"></div>
    <div class="layer layer3"></div>
    <div class="layer layer4"></div>
  </div>
</template>

<script>
export default {
  name: "DotsBackground",
};
</script>

<style>
.background-dots {
  position: fixed;
  inset: 0;
  background: #123;
  overflow: hidden;
  z-index: -1;
}

/* Each layer is just a container; the pseudo-element draws the dots */
.layer::before {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 3em;
  height: 3em;
  content: '.';
  font-size: 52px;
  color: transparent;
  mix-blend-mode: screen;
  animation: move infinite ease-in-out alternate;
}

/* Pre-baked stars (add ~40 per layer for density) */
.layer1::before {
  text-shadow:
    1em 1em 7px hsla(200,100%,70%,.9),
    -1.2em -0.5em 7px hsla(120,100%,60%,.9),
    0.5em -1.8em 7px hsla(330,100%,70%,.9),
    1.9em 0.6em 7px hsla(45,100%,65%,.9),
    -2em 1em 7px hsla(300,100%,60%,.9);
  animation-duration: 44s;
  animation-delay: -27s;
}

.layer2::before {
  text-shadow:
    -0.9em 2em 7px hsla(180,100%,60%,.9),
    2em -1.1em 7px hsla(300,100%,65%,.9),
    -2.1em 0.4em 7px hsla(90,100%,55%,.9),
    1.2em 1.9em 7px hsla(30,100%,60%,.9),
    -2.3em -0.7em 7px hsla(240,100%,65%,.9);
  animation-duration: 43s;
  animation-delay: -32s;
}

.layer3::before {
  text-shadow:
    1.3em -1.3em 7px hsla(60,100%,55%,.9),
    -2.2em 0.7em 7px hsla(330,100%,70%,.9),
    0.6em 1.9em 7px hsla(120,100%,55%,.9),
    -1.8em -0.9em 7px hsla(200,100%,65%,.9),
    2.1em 1.2em 7px hsla(270,100%,60%,.9);
  animation-duration: 42s;
  animation-delay: -23s;
}

.layer4::before {
  text-shadow:
    -1.1em 1.3em 7px hsla(150,100%,55%,.9),
    2.0em -1.0em 7px hsla(45,100%,55%,.9),
    -2.3em 0.5em 7px hsla(210,100%,65%,.9),
    1.2em -1.8em 7px hsla(300,100%,60%,.9),
    0.7em 2.2em 7px hsla(90,100%,55%,.9);
  animation-duration: 41s;
  animation-delay: -19s;
}

@keyframes move {
  from {
    transform: rotate(0deg) scale(12) translateX(-20px);
  }
  to {
    transform: rotate(360deg) scale(18) translateX(20px);
  }
}
</style>
