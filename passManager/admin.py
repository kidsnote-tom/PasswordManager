from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.contrib.admin import SimpleListFilter

from passManager.models import passDb


class LoginsFilter(SimpleListFilter):
    """ Filter based on same login name.
    Make facer of login number with 3 or more
    login name ocurrences
    """
    title = "TOP Logins"
    parameter_name = "logins"
    # Get all objects
    rows = passDb.objects.all()                                                                                                                                                      
    # Logins list                                                                                                                                                     
    logins = []                                                                                                                                                                      
    for row in rows:
        logins.append(row.login)                                                                                                                                                     
    # Duplicate clean
    logins = set(logins)                                                                                                                                                             
    
    # Get tuple with login and ocurences
    lista = {}
    for l in set(logins):
        numrows = passDb.objects.filter(login=l).count()                                                                                                                                      
        if numrows > 2:
            lista[str(l)] = numrows                                                                                                                                                  
                                                                                                                                                                                 
    # Import module for order dictionary                                                                                                                                                
    from operator import itemgetter                                                                                                                                                  
    slist = sorted(lista.items(), key=itemgetter(1), reverse=True)                                                                                                                   
    
    # Generate facetes
    facet = []                                                                                                                                                                       
    for n in range(0 ,(len(slist))):
        facet.append(((slist[n][0]),(slist[n][0]+' ('+str(slist[n][1]))+')'))
    
    def lookups(self, request, model_admin):
        return (
                self.facet
                )
        
    def queryset(self, request, queryset):
        for n in range(0 ,(len(self.slist))):
            val = self.slist[n][0]
            if self.value() == val:
                return queryset.filter(login=val)

class ServersFilter(SimpleListFilter):
    """ Filter based on same server name.
    Make facet of server names number with 3 or more
    name ocurrences
    """
    title = 'TOP Servers'
    parameter_name = 'servers'
    # Get all objects
    rows = passDb.objects.all()
    # Server list
    servers = []
    for row in rows:
        servers.append(row.server)
    # Duplicate clean
    # servers = set(servers)

    # Get tuple with servers and ocurences
    lista = {}
    for l in set(servers):
        numrows = passDb.objects.filter(server=l).count()
        if numrows >= 1:
            lista[str(l)] = numrows

    # Import module for order dictionary
    from operator import itemgetter
    slist = sorted(lista.items(), key=itemgetter(1), reverse=True)

    # Generate facets
    facet = []
    for n in range(0 ,(len(slist))):
        facet.append(((slist[n][0]),(slist[n][0]+' ('+str(slist[n][1]))+')'))

    def lookups(self, request, model_admin):
        return (self.facet)

    def queryset(self, request, queryset):
        for n in range(0 ,(len(self.slist))):
            val = self.slist[n][0]
            if self.value() == val:
                return queryset.filter(server=val)

class PassManagerAdmin(admin.ModelAdmin):
    class Media:
        js = ("jquery-1.7.1.min.js", "jquery-ui-1.8.18.custom.min.js", "functions.js",)
        css = {
            "all": ("jquery-ui-1.8.18.custom.css",)
        }

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'40'})},
        #models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':60})},
    }

    ordering = ['creation_date']

    list_per_page = 30
    actions = ['export_as_json']
    actions_on_bottom = True
    actions_on_top = False
    list_display_links = ['name']
    list_display = ('name','login','getClickMe','server','uploader','creation_date','notes','send_email_html')
    list_editable = []
    date_hierarchy = 'creation_date'
    save_as = True
    readonly_fields = [
        'creation_date',
        "uploader"
    ]

    list_filter = (LoginsFilter, ServersFilter, 'uploader','creation_date')
    fieldsets = [
		    (None,         {'fields': ['name',('login','password'),'server','notes']}),
		    ]

    search_fields = ['name','login','server','notes']
        
    def save_model(self, request, obj, form, change):
        #obj.password = passEncr('encrypt', obj.password)
        obj.uploader = request.user
        obj.nivel = 1
        obj.save()
    
    def send_email_html(self, queryset):
        buttons = """                                                                                                                                                            
            <div style="width:20px">                                                                                                                                             
            <a href="/send_pass/%s" title="Enviar por Email" name="Envio de Correo" class="mailwindow"><img src="/static/mail-message-new.png"></img></a>                       
            </div>
        """ % (queryset.id)
        return buttons
    send_email_html.short_description = ''
    send_email_html.allow_tags = True
    
    def export_as_json(self, request, queryset):
        from django.http import HttpResponse
        from django.core import serializers
        response = HttpResponse(mimetype="text/javascript")
        serializers.serialize("json", queryset, stream=response)
        return response

        
admin.site.register(passDb, PassManagerAdmin)
