<template>
  <div >
<!--    <div  v-if="this.in_viewport">-->
    <jupyter-widget  v-for="child in children" :key="child" :widget="child"></jupyter-widget>
<!--    </div>-->
  </div></template>

<script>
module.exports = {
  data() {
    return {
      "cell": undefined,
      "in_viewport": true,
      "element_pixel_size": {"width": 0, "height": 0}
    }
  },
  computed: {
  },
  created() {
    function debounce(f, delay) {
      let timer = 0;
      return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => f.apply(this, args), delay);
      }
    }
    this.cellDisplayObserver = new MutationObserver(debounce(mutationsList => {
      for (const mutation of mutationsList) {
            if (mutation.type === 'attributes' && (mutation.attributeName === 'style')) {
              this._updateDisplay(mutation.target);
            }
        }
    }, this.in_viewport_delay));
    this.cellResizeObserver = new ResizeObserver(debounce(entries => {
      this._updateSize();
    }, this.in_viewport_delay));
  },
  mounted() {
    // console.log("el: ", this.$el.parentElement);
    //
    this.cell = this.$el.parentElement.closest(".jp-Cell")
    // console.log("cell: ", this.cell);
    this._updateDisplay(this.cell);
    this.cellDisplayObserver.observe(this.cell, { attributes: true, attributeFilter: ['style'] });
    this.cellResizeObserver.observe(this.cell);
  },
  destroyed() {
    this.cellDisplayObserver.disconnect();
    this.cellResizeObserver.disconnect();
  },
  methods: {
    _updateDisplay(target) {
      if (target.style.display === 'none' || target.style.opacity === '0') {
        this.in_viewport = false;
        // console.log('hidden: ' + this.uuid);
      } else {
        this.in_viewport = true;
        // console.log('shown: ' + this.uuid);
      }
    },
    _updateSize() {
      const element_pixel_size = (({ width, height }) => ({ width, height }))(this.$el.getBoundingClientRect());
      if (element_pixel_size.width != 0 && element_pixel_size.height != 0) {
        this.element_pixel_size = element_pixel_size;
        // console.log('element_pixel_size:')
        // console.log(this.element_pixel_size)
      }
      // console.log(target.getBoundingClientRect())
      // console.log(target)
    },
    // _updateDisplay(target) {
    //   // console.log("Mutation observed: ", mutation);
    //   if (target.style.display === "none" || target.style.opacity === "0") {
    //     // If the display is set to none or opacity is 0, we consider it not in viewport
    //     console.log('hidden: ' + this.element_id)
    //     this.in_viewport = false;
    //   } else {
    //     // Otherwise, we consider it in viewport
    //     console.log('shown: ' + this.element_id)
    //     this.in_viewport = true;
    //   }
    // },
  },
}
</script>

<style id="output"></style>