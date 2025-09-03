<template>
  <div class="omnipy-hidden">
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

  watch: {
    font_size: function () {
      this._updateViewData();
      },
    font_weight: function () {
      this._updateViewData();
    },
    font_family: function () {
      this._updateViewData();
    },
    line_height: function () {
      this._updateViewData();
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
    this.windowPanel = document.getElementsByClassName('jp-WindowedPanel')[0];
    this.resizeObserverWidth.observe(this.$el);
    this.resizeObserverHeight.observe(this.windowPanel);
    this._preventCellCollapse();
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
        this.available_display_dims = {"width": width, "height": height};
      }
    },
    _getColumns(width) {
      return Math.floor(width / this.charWidth);
    },
    _getLines(height) {
      return Math.floor(height / this.charHeight);
    },
    _preventCellCollapse() {
      let cell = this.$el.closest(".jp-Cell")

      if (cell && !cell.classList.contains('getsize-protected-cell')) {
        cell.classList.add('getsize-protected-cell');
      }
    },
  },
}
</script>

<style id="output"></style>