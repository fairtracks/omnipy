<template>
  <div class="omnipy-hidden">
    <jupyter-widget v-for="child in children" :key="child" :widget="child"></jupyter-widget>
  </div></template>

<script>
module.exports = {
  created() {
    function debounce(f, delay) {
      let timer = 0;
      return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => f.apply(this, args), delay);
      }
    }
    this.bgColorObserver = new MutationObserver(debounce(mutationsList => {
      for (const mutation of mutationsList) {
            if (mutation.type === 'attributes' && (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
                this._updateBgColor();
            }
        }
    }, this.update_delay));
  },
  mounted() {
    this.bgColorObserver.observe(document.body, { attributes: true, attributeFilter: ['style', 'class'] });
    this._updateBgColor();
  },
  destroyed() {
    this.bgColorObserver.disconnect();
  },
  methods: {
    _updateBgColor() {
        this.bg_color = window.getComputedStyle(document.body).getPropertyValue("background-color");
    },
  },
}
</script>

<style id="output"></style>