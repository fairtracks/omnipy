<template>
  <div class="omnipy-hidden">
    <jupyter-widget v-for="child in children" :key="child" :widget="child"></jupyter-widget>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      "windowPanel": undefined,
    }
  },
  created() {
    function debounce(f, delay) {
      let timer = 0;
      return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => f.apply(this, args), delay);
      }
    }
    this.resizeObserverWidth = new ResizeObserver(debounce(entries => {
      this.updateViewData();
    }, this.resize_delay));
    this.resizeObserverHeight = new ResizeObserver(debounce(entries => {
      this.updateViewData();
    }, this.resize_delay));
  },
  mounted() {
    this.windowPanel = document.getElementsByClassName('jp-WindowedPanel')[0];
    this.resizeObserverWidth.observe(this.$el);
    this.resizeObserverHeight.observe(this.windowPanel);
    this.preventCellCollapse();
  },
  destroyed() {
    this.resizeObserverWidth.unobserve(this.$el);
    this.resizeObserverHeight.unobserve(this.windowPanel);
  },
  methods: {
    updateViewData() {
      const width = this.$el.getBoundingClientRect().width;
      const height = this.windowPanel.getBoundingClientRect().height;
      if (width && height) {
        this.available_display_dims_in_px = {"width": width, "height": height};
      }
    },
    preventCellCollapse() {
      let cell = this.$el.closest(".jp-Cell")

      if (cell && !cell.classList.contains('getsize-protected-cell')) {
        cell.classList.add('getsize-protected-cell');
      }
    },
  },
}
</script>

<style id="output"></style>