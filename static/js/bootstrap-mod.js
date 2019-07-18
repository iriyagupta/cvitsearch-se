Noty.overrideDefaults({
  callbacks: {
    onTemplate: function() {
      if (this.options.type === 'reply') {
        this.barDom.innerHTML = '<p class="noty-reply">' + this.options.text + '</p>';
      }
    }
  }
})