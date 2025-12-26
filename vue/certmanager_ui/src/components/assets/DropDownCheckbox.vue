<template>
  <div ref="dropdownRef" class="dropdown-container">
    <!-- Trigger button -->
    <button style="" class="dropdown-button" @click="toggleDropdown">
      {{ selectedText || placeholder }}
      <span class="arrow">&#9662;</span>
    </button>

    <!-- Dropdown list -->
    <div v-if="open" class="dropdown-list">
        <div class="holder">

        
      <button
        v-for="option in opts"
        :key="option.emitValue"
        class="dropdown-item"
        @click="selectOption(option)"
      >
          <input style="vertical-align: middle;" type="checkbox" id="something" v-model="already_opts"
  :value="option.emitValue" />
        {{ option.displayName }}
      </button>
    </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'DropDownCheckbox',
  props: {
    options: { type: Array, required: true },
    already_selected: { type: Array, required: true },
    placeholder: { type: String, default: 'Select an option' }
  },
  data () {
    return {
      opts: [],
      already_opts: [],
      open: false,
      selectedText: `${this.already_selected.length} selected`,
    }
  },
  mounted() {
    this.opts = this.options
    this.already_opts = [...this.already_selected]
  },
  emits: ['update:modelValue', 'updateFilter'],
  methods: {
    toggleDropdown() {
      this.open = !this.open
    },
    selectOption(option) {
      const index = this.already_opts.indexOf(option.emitValue)
      if (index > -1) {
        this.already_opts.splice(index, 1)
      } else {
        this.already_opts.push(option.emitValue)
      }

      this.selectedText = `${this.already_opts.length} selected`

      this.$emit('update:modelValue', this.already_opts)
      this.$emit('updateFilter', this.already_opts)
    }
  }
}
</script>


<style scoped>
/* Container */
.dropdown-container {
  position: relative;
  width: 300px; /* adjust as needed */
  font-family: sans-serif;
  margin-top: 0px;

}

/* Trigger button */
.dropdown-button {
  width: 100%;
  padding: 10px 15px;
  text-align: left;
  border-radius: 0px;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;

  border-radius: 5px;
  font-size: 16px;
  font-weight: 500;
  color: #fff; /* White text works best on glass */
  cursor: pointer;
  text-align: center;

  /* Glass background */
              background: linear-gradient(
    to bottom right,
    rgba(255,255,255,0.6),
    rgba(255,255,255,0) 70%
  );
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);

  /* Frosted border */
  border: 1px solid rgba(255, 255, 255, 0.3);

  /* Glow */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  
}

/* Arrow icon */
.arrow {
  font-size: 0.7em;
  margin-left: 8px;
}

/* Dropdown list */
.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
  /*box-shadow: 0 2px 6px rgba(0,0,0,0.15);*/
  z-index: 100;
  margin-top: 0px;
  display: flex;
  flex-direction: column;


  border-radius: 5px;
  font-size: 16px;
  font-weight: 500;
  color: #fff; /* White text works best on glass */
  cursor: pointer;
  text-align: center;
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);


  /* Frosted border */
  border: 1px solid rgba(255, 255, 255, 0.3);

  /* Glow */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  max-height: 200px;
  overflow-y: scroll;
}

/* Each item */
.dropdown-item {
  padding: 4px 12px;
  background: #fff;
  cursor: pointer;
  width: calc(100% - 5px);
  border: solid 1px lightgrey;

    padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  color: #464545; /* White text works best on glass */
  cursor: pointer;
  text-align: left;


    border-radius: 5px;
    margin: 3px;
    font-size: 0.8em;

      /* Glass background */
  background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.765),
        rgba(255, 255, 255, 0.385) 90%);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);

  /* Frosted border */
  border: 1px solid rgba(255, 255, 255, 0.3);

  /* Glow */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  /* Smooth transition */
  transition: all 0.3s ease;
}

.dropdown-item:last-child {
  border-bottom: none;
}

/* Hover effect */
.dropdown-item:hover {
  background-color: #f0f0f0;
  color: rgb(176, 176, 176);
}


 div.holder {
    text-align: left;
    border-radius: 7px;
    /* Apple Glassmorphism base */
    background: linear-gradient(to bottom right,
        rgba(255, 255, 255, 0.6),
        rgba(255, 255, 255, 0) 70%);
    width: fit-content;
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);

    /* Subtle borders */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Optional shadow for depth */
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);

    /* Smooth scroll for nice feel */
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    padding: 10px;
    margin-top:0px;
    display: inline-block;
  }

  div.holder::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: rgba(255, 255, 255, 0.25); /* Dark tint */
  pointer-events: none;
}

input[type="checkbox"] {
  appearance: none;        /* Modern browsers */
  -webkit-appearance: none; /* Safari/older WebKit */
  -moz-appearance: none;    /* Firefox */
  
  width: 20px;
  height: 20px;
  border: 2px solid #333;
  border-radius: 4px;
  cursor: pointer;
}


input[type="checkbox"]:checked::before {
  content: "";
  display: block;
  width: 10px;
  height: 10px;
  margin: 3px auto;
  border-radius: 2px;
  background: rgb(58, 58, 58);
}
</style>
