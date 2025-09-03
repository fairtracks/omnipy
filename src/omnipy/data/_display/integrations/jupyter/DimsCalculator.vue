<template>
  <div class="asdf">
    <jupyter-widget v-for="child in children" :key="child" :widget="child"></jupyter-widget>
  </div>
</template>

<script>
module.exports = {
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
  mounted() {
    this.updateViewData();
  },
  watch: {
    available_display_dims_in_px: function () {
      this.updateViewData();
    },
    font_size: function () {
      this.updateViewData();
      },
    font_weight: function () {
      this.updateViewData();
    },
    font_family: function () {
      this.updateViewData();
    },
    line_height: function () {
      this.updateViewData();
    },
  },
  methods: {
    updateViewData() {
      const width = this.getColumns(this.available_display_dims_in_px.width);
      const height = this.getLines(this.available_display_dims_in_px.height);
      if (width && height) {
        console.log("Updating available display dims:", width, height);
        this.available_display_dims = {"width": width, "height": height};
      }
    },
    getColumns(width) {
      return Math.floor(width / this.charWidth);
    },
    getLines(height) {
      return Math.floor(height / this.charHeight);
    },
  },
}
</script>

<style id="output"></style>