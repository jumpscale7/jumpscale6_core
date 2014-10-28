class Popup(object):
    def __init__(self, id, submit_url, header='', action_button='Save', form_layout=''):
        self.widgets = []
        self.id = id
        self.form_layout = form_layout
        self.header = header
        self.action_button = action_button
        self.submit_url = submit_url

        import jinja2
        self.jinja = jinja2.Environment(variable_start_string="${", variable_end_string="}")

    def addText(self, label, name, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <input type="text" class="form-control" name="${name}" {% if required %}required{% endif %}>
              </div>
        ''')
        content = template.render(label=label, name=name)
        self.widgets.append(content)

    def addHiddenField(self, name, value):
        template = self.jinja.from_string('''
            <input type="hidden" class="form-control" name="${name}" value="${value}">
        ''')
        content = template.render(value=value, name=name)
        self.widgets.append(content)

    def addTextArea(self, label, name, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <textarea class="form-control" name="${name}" {% if required %}required{% endif %}>
              </div>
        ''')
        content = template.render(label=label, name=name)
        self.widgets.append(content)

    def addNumber(self, label, name, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <input type="number" class="form-control" name="${name}" {% if required %}required{% endif %}>
              </div>
        ''')
        content = template.render(label=label, name=name)
        self.widgets.append(content)

    def addDropdown(self, label, name, options, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <select class="form-control" name="${name}" {% if required %}required{% endif %}>
                    {% for title, value in options %}
                        <option value="${value}">${title}</option>
                    {% endfor %}
                </select>
              </div>
        ''')
        content = template.render(label=label, name=name, options=options)
        self.widgets.append(content)

    def addRadio(self, label, name, options, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only">${label}</label>
                {% for title, value in options %}
                    <label>
                        <input type="radio" name="${name}" value="${value}" {% if required %}required{% endif %}>
                            ${title}
                        </input>
                    </label>
                {% endfor %}
              </div>
        ''')
        content = template.render(label=label, name=name, options=options)
        self.widgets.append(content)

    def addCheckboxes(self, label, name, options):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only">${label}</label>
                {% for title, value in options %}
                    <label class="checkbox">
                      <input type="checkbox" name="${name}_${loop.index}" value="${value}" />
                      ${title}
                    </label>
                {% endfor %}
            </div>
        ''')
        content = template.render(label=label, name=name, options=options)
        self.widgets.append(content)

    def write_html(self, page):
        template = self.jinja.from_string('''
            <form role="form" method="post" action="${submit_url}" class="popup_form">
            <div id="${id}" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="${id}Label" aria-hidden="true">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>
                <div id="${id}Label" class="modal-header-text">${header}</div>
              </div>
              <div class="modal-body modal-body-error alert alert-error">
                Error happened on the server
              </div>
              <div class="modal-body modal-body-form">
                {% for widget in widgets %}${widget}{% endfor %}
              </div>
              <div class="modal-footer">
                <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
                <button class="btn btn-primary" data-loading-text="Loading...">${action_button}</button>
              </div>
            </div>
        </form>
        ''')
        
        content = template.render(id=self.id, header=self.header, action_button=self.action_button, form_layout=self.form_layout, 
                                widgets=self.widgets, submit_url=self.submit_url)

        css = '.modal-body-error { display: none } .modal-header-text { font-weight: bold; font-size: 24.5px; line-height: 30px; }'
        if css not in page.head:
            page.addCSS(cssContent=css)

        jsLink = '/jslib/old/jquery.form/jquery.form.js'
        if jsLink not in page.head:
            page.addJS(jsLink)

        js = '''$(function(){
            $('.popup_form').ajaxForm({
                clearForm: true,
                beforeSubmit: function(formData, $form, options) {
                    this.popup = $form;
                    $form.find('.modal-footer > .btn-primary').button('loading');
                    $form.find("input,select,textarea").prop("disabled", true)
                },
                success: function(responseText, statusText, xhr) {
                    this.popup.find('.modal').modal('hide');
                    this.popup.find('.modal-body').hide();
                    this.popup.find('.modal-body-form').show();

                },
                error: function(responseText, statusText, xhr, $form) {
                    if (responseText) {
                        this.popup.find('.modal-body-error').text(responseText.responseText);
                    }
                    this.popup.find('.modal-body').hide();
                    this.popup.find('.modal-footer > .btn-primary').hide();
                    this.popup.find('.modal-body-error').show();
                }
            });
            $('.modal').on('hidden', function() {
                $(this).find("input,select,textarea").prop("disabled", false)
                $(this).find('.modal-footer > .btn-primary').button('reset').show();
                $(this).find('.modal-body').hide();
                $(this).find('.modal-body-form').show();
            });
        });'''

        if js not in page.head:
            page.addJS(jsContent=js)
        
        page.addMessage(content)
