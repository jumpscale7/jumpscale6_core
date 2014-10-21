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
                <input type="text" class="form-control" id="${name}" {% if required %}required{% endif %}>
              </div>
        ''')
        content = template.render(label=label, name=name)
        self.widgets.append(content)

    def addTextArea(self, label, name, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <textarea class="form-control" id="${name}" {% if required %}required{% endif %}>
              </div>
        ''')
        content = template.render(label=label, name=name)
        self.widgets.append(content)

    def addNumber(self, label, name, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <input type="number" class="form-control" id="${name}" {% if required %}required{% endif %}>
              </div>
        ''')
        content = template.render(label=label, name=name)
        self.widgets.append(content)

    def addDropdown(self, label, name, options, required=False):
        template = self.jinja.from_string('''
            <div class="form-group">
                <label class="sr-only" for="${name}">${label}</label>
                <select class="form-control" id="${name}" {% if required %}required{% endif %}>
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
                      <input type="checkbox" id="${name}_${loop.index}" value="${value}" />
                      ${title}
                    </label>
                {% endfor %}
            </div>
        ''')
        content = template.render(label=label, name=name, options=options)
        self.widgets.append(content)

    def to_html(self):
        template = self.jinja.from_string('''
            <form role="form" method="post" target="${submit_url}" class="popup_form">
            <div id="${id}" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="${id}Label" aria-hidden="true">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>
                <h3 id="${id}Label">${header}</h3>
              </div>
              <div class="modal-body modal-body-sending">
                Sending...
              </div>
              <div class="modal-body modal-body-error">
                Error happened on the server
              </div>
              <div class="modal-body modal-body-form">
                {% for widget in widgets %}${widget}{% endfor %}
              </div>
              <div class="modal-footer">
                <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
                <button class="btn btn-primary">${action_button}</button>
              </div>
            </div>
        </form>
        <style>
            .modal-body-sending, .modal-body-error { display: none }
        </style>
        <script src="/jslib/old/jquery.form/jquery.form.js"></script>
        <script type="text/javascript">
        $(function(){
            $('.popup_form').ajaxForm({
                clearForm: true,
                beforeSubmit: function() {
                    $('.popup_form').find('.modal-body').hide();
                    $('.popup_form').find('.modal-body-sending').show();
                },
                success: function(data) {
                    $('#${id}').modal('hide');
                    $('.popup_form').find('.modal-body').hide();
                    $('.popup_form').find('.modal-body-form').show();
                },
                error: function() {
                    $('.popup_form').find('.modal-body').hide();
                    $('.popup_form').find('.modal-body-error').show();
                }
            });
        });
        </script>
        ''')
        content = template.render(id=self.id, header=self.header, action_button=self.action_button, form_layout=self.form_layout, 
                                widgets=self.widgets, submit_url=self.submit_url)
        return content


