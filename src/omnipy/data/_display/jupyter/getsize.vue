<template>
  <div>
    <jupyter-widget v-for="child in children" :key="child" :widget="child"></jupyter-widget>
  </div></template>

<script>
module.exports = {
  data() {
    return {
      "windowPanel": undefined,
    }
  },
  computed: {
    charWidth() {
      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      context.font = `${this.font_weight} ${this.font_size}px ${this.font_family}`;
      return context.measureText('a').width;
    },
    charHeight() {
      return this.font_size * this.line_height;
    },
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
      this._updateViewData();
    }, this.resize_delay));
    this.resizeObserverHeight = new ResizeObserver(debounce(entries => {
      this._updateViewData();
    }, this.resize_delay));
  },
  mounted() {
    this.windowPanel = this.$el.closest(".jp-WindowedPanel-outer");
    this.resizeObserverWidth.observe(this.$el);
    this.resizeObserverHeight.observe(this.windowPanel);
  },
  destroyed() {
    this.resizeObserverWidth.unobserve(this.$el);
    this.resizeObserverHeight.unobserve(this.windowPanel);
  },
  methods: {
    _updateViewData() {
      const width = this._getColumns(this.$el.getBoundingClientRect().width);
      const height = this._getLines(this.windowPanel.getBoundingClientRect().height);
      if (width && height) {
        this.console_size = {"width": width, "height": height};
      }
    },

    _getColumns(width) {
      return Math.floor(width / (this.charWidth));
    },
    _getLines(height) {
      return Math.floor(height / this.charHeight);
    },
  },
}
</script>

<style id="output"></style>