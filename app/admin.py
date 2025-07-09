"""
Configuración del panel de administración para el sistema Aurora.

Este módulo contiene todas las configuraciones personalizadas para el
panel de administración de Django, incluyendo:
- Configuraciones de visualización de listas
- Filtros y búsquedas avanzadas
- Acciones personalizadas
- Configuraciones de formularios
- Permisos y validaciones

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Area, Cargo, Empleados, EmpleadosProyecto, Estados, 
    Prioridad, Proyecto, Subtarea, Tareas
)


# Configuración global del sitio de administración
admin.site.site_header = "Sistema Aurora - Administración"
admin.site.site_title = "Aurora Admin"
admin.site.index_title = "Panel de Administración"


class BaseModelAdmin(admin.ModelAdmin):
    """
    Clase base para todas las configuraciones de admin.
    """
    save_on_top = True
    list_per_page = 25
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer campos de timestamp de solo lectura."""
        readonly = list(super().get_readonly_fields(request, obj))
        if hasattr(self.model, 'fecha_creacion'):
            readonly.extend(['fecha_creacion', 'fecha_actualizacion'])
        return readonly


@admin.register(Estados)
class EstadosAdmin(BaseModelAdmin):
    """
    Configuración del admin para Estados.
    """
    list_display = ['nombre_estado', 'activo', 'fecha_creacion_formatted', 'usar_count']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre_estado', 'descripcion']
    ordering = ['nombre_estado']
    list_editable = ['activo']
    
    fieldsets = (
        (None, {
            'fields': ('nombre_estado', 'descripcion', 'activo')
        }),
        ('Información de timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def fecha_creacion_formatted(self, obj):
        """Formatear fecha de creación."""
        return obj.fecha_creacion.strftime('%d/%m/%Y %H:%M')
    fecha_creacion_formatted.short_description = 'Fecha Creación'
    fecha_creacion_formatted.admin_order_field = 'fecha_creacion'
    
    def usar_count(self, obj):
        """Mostrar cuántas entidades usan este estado."""
        areas = obj.area_set.count()
        empleados = obj.empleados_set.count()
        proyectos = obj.proyecto_set.count()
        tareas = obj.tareas_set.count()
        total = areas + empleados + proyectos + tareas
        return format_html(
            '<span style="color: {};">{}</span>',
            'red' if total == 0 else 'green',
            total
        )
    usar_count.short_description = 'Usos'
    
    actions = ['activar_estados', 'desactivar_estados']
    
    def activar_estados(self, request, queryset):
        """Acción para activar estados seleccionados."""
        count = queryset.update(activo=True)
        self.message_user(request, f'{count} estados activados exitosamente.')
    activar_estados.short_description = "Activar estados seleccionados"
    
    def desactivar_estados(self, request, queryset):
        """Acción para desactivar estados seleccionados."""
        count = queryset.update(activo=False)
        self.message_user(request, f'{count} estados desactivados exitosamente.')
    desactivar_estados.short_description = "Desactivar estados seleccionados"


@admin.register(Prioridad)
class PrioridadAdmin(BaseModelAdmin):
    """
    Configuración del admin para Prioridad.
    """
    list_display = ['nombre_prioridad', 'nivel', 'color_preview', 'activo', 'proyectos_count', 'tareas_count']
    list_filter = ['activo', 'nivel']
    search_fields = ['nombre_prioridad']
    ordering = ['nivel']
    list_editable = ['activo']
    
    def color_preview(self, obj):
        """Mostrar preview del color."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def proyectos_count(self, obj):
        """Contar proyectos con esta prioridad."""
        return obj.proyecto_set.count()
    proyectos_count.short_description = 'Proyectos'
    
    def tareas_count(self, obj):
        """Contar tareas con esta prioridad."""
        return obj.tareas_set.count()
    tareas_count.short_description = 'Tareas'


@admin.register(Cargo)
class CargoAdmin(BaseModelAdmin):
    """
    Configuración del admin para Cargo.
    """
    list_display = ['nombre_cargo', 'nivel_jerarquico', 'salario_base_formatted', 'activo', 'empleados_count']
    list_filter = ['activo', 'nivel_jerarquico']
    search_fields = ['nombre_cargo', 'descripcion']
    ordering = ['nivel_jerarquico', 'nombre_cargo']
    list_editable = ['activo']
    
    fieldsets = (
        (None, {
            'fields': ('nombre_cargo', 'descripcion', 'nivel_jerarquico', 'activo')
        }),
        ('Información Salarial', {
            'fields': ('salario_base',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def salario_base_formatted(self, obj):
        """Formatear salario base."""
        if obj.salario_base:
            return f"${obj.salario_base:,.2f}"
        return "No especificado"
    salario_base_formatted.short_description = 'Salario Base'
    salario_base_formatted.admin_order_field = 'salario_base'
    
    def empleados_count(self, obj):
        """Contar empleados con este cargo."""
        count = obj.empleados_set.filter(is_active=True).count()
        return format_html(
            '<a href="{}?cargo__id__exact={}">{} empleados</a>',
            reverse('admin:app_empleados_changelist'),
            obj.id_cargo,
            count
        )
    empleados_count.short_description = 'Empleados Activos'


class EmpleadosInline(admin.TabularInline):
    """
    Inline para mostrar empleados en áreas.
    """
    model = Empleados
    extra = 0
    fields = ['nombres', 'apellidos', 'cargo', 'is_active']
    readonly_fields = ['nombres', 'apellidos', 'cargo']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Area)
class AreaAdmin(BaseModelAdmin):
    """
    Configuración del admin para Area.
    """
    list_display = ['nombre_area', 'responsable_link', 'estado', 'empleados_count', 'proyectos_count']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['nombre_area', 'descripcion_area']
    ordering = ['nombre_area']
    inlines = [EmpleadosInline]
    
    fieldsets = (
        (None, {
            'fields': ('nombre_area', 'descripcion_area', 'estado')
        }),
        ('Gestión', {
            'fields': ('responsable',),
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def responsable_link(self, obj):
        """Link al responsable del área."""
        if obj.responsable:
            url = reverse('admin:app_empleados_change', args=[obj.responsable.id_empleado])
            return format_html('<a href="{}">{}</a>', url, obj.responsable.nombre_completo)
        return "Sin asignar"
    responsable_link.short_description = 'Responsable'
    
    def empleados_count(self, obj):
        """Contar empleados activos en el área."""
        count = obj.empleados.filter(is_active=True).count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'red',
            count
        )
    empleados_count.short_description = 'Empleados'
    
    def proyectos_count(self, obj):
        """Contar proyectos del área."""
        count = Proyecto.objects.filter(responsable__area=obj).count()
        return count
    proyectos_count.short_description = 'Proyectos'


@admin.register(Empleados)
class EmpleadosAdmin(UserAdmin):
    """
    Configuración del admin para Empleados (Usuario personalizado).
    """
    list_display = ['login', 'nombre_completo', 'correo_electronico', 'area', 'cargo', 'is_active', 'fecha_ingreso']
    list_filter = ['is_active', 'is_staff', 'area', 'cargo', 'estado', 'fecha_ingreso']
    search_fields = ['nombres', 'apellidos', 'correo_electronico', 'login', 'celular']
    ordering = ['apellidos', 'nombres']
    list_editable = ['is_active']
    
    fieldsets = (
        (None, {
            'fields': ('login', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'correo_electronico', 'celular', 'fecha_nacimiento')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'area', 'estado', 'fecha_ingreso')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'correo_electronico', 'celular')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'area', 'estado')
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'last_login', 'uuid']
    
    def nombre_completo(self, obj):
        """Mostrar nombre completo."""
        return obj.nombre_completo
    nombre_completo.short_description = 'Nombre Completo'
    nombre_completo.admin_order_field = 'apellidos'
    
    actions = ['activar_empleados', 'desactivar_empleados', 'export_empleados']
    
    def activar_empleados(self, request, queryset):
        """Activar empleados seleccionados."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} empleados activados exitosamente.')
    activar_empleados.short_description = "Activar empleados seleccionados"
    
    def desactivar_empleados(self, request, queryset):
        """Desactivar empleados seleccionados."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} empleados desactivados exitosamente.')
    desactivar_empleados.short_description = "Desactivar empleados seleccionados"


class TareasInline(admin.TabularInline):
    """
    Inline para mostrar tareas en proyectos.
    """
    model = Tareas
    extra = 0
    fields = ['nombre', 'asignado_a', 'prioridad', 'completada', 'fecha_fin_estimada']
    readonly_fields = []


@admin.register(Proyecto)
class ProyectoAdmin(BaseModelAdmin):
    """
    Configuración del admin para Proyecto.
    """
    list_display = ['nombre', 'responsable', 'estado', 'prioridad', 'progreso_bar', 'dias_restantes', 'presupuesto_formatted']
    list_filter = ['estado', 'prioridad', 'fecha_inicio', 'responsable__area']
    search_fields = ['nombre', 'descripcion', 'responsable__nombres', 'responsable__apellidos']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_inicio'
    inlines = [TareasInline]
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'responsable')
        }),
        ('Fechas y Duración', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real', 'duracion_estimada')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad')
        }),
        ('Presupuesto', {
            'fields': ('presupuesto',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('uuid', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['uuid', 'fecha_creacion', 'fecha_actualizacion']
    
    def progreso_bar(self, obj):
        """Mostrar barra de progreso."""
        progreso = obj.progreso_temporal
        color = 'red' if progreso < 30 else 'orange' if progreso < 70 else 'green'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}px; background-color: {}; height: 20px; border-radius: 3px; text-align: center; line-height: 20px; color: white; font-size: 11px;">'
            '{}%</div></div>',
            int(progreso),
            color,
            int(progreso)
        )
    progreso_bar.short_description = 'Progreso'
    
    def dias_restantes(self, obj):
        """Calcular días restantes."""
        if obj.fecha_fin_estimada:
            dias = (obj.fecha_fin_estimada - timezone.now().date()).days
            color = 'red' if dias < 0 else 'orange' if dias < 7 else 'green'
            return format_html('<span style="color: {};">{}</span>', color, dias)
        return "N/A"
    dias_restantes.short_description = 'Días Restantes'
    
    def presupuesto_formatted(self, obj):
        """Formatear presupuesto."""
        if obj.presupuesto:
            return f"${obj.presupuesto:,.2f}"
        return "No especificado"
    presupuesto_formatted.short_description = 'Presupuesto'
    presupuesto_formatted.admin_order_field = 'presupuesto'


class SubtareasInline(admin.TabularInline):
    """
    Inline para mostrar subtareas en tareas.
    """
    model = Subtarea
    extra = 0
    fields = ['nombre_subtarea', 'asignado_a', 'completada', 'fecha_fin_estimada']


@admin.register(Tareas)
class TareasAdmin(BaseModelAdmin):
    """
    Configuración del admin para Tareas.
    """
    list_display = ['nombre', 'proyecto', 'asignado_a', 'prioridad', 'estado_completado', 'fecha_fin_estimada']
    list_filter = ['completada', 'prioridad', 'proyecto', 'asignado_a__area']
    search_fields = ['nombre', 'descripcion', 'proyecto__nombre']
    ordering = ['prioridad__nivel', 'fecha_fin_estimada']
    date_hierarchy = 'fecha_inicio'
    inlines = [SubtareasInline]
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'proyecto', 'asignado_a')
        }),
        ('Tiempos', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real', 'duracion_estimada', 'duracion_real')
        }),
        ('Estado', {
            'fields': ('estado', 'prioridad', 'completada')
        }),
        ('Sistema', {
            'fields': ('uuid', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['uuid', 'fecha_creacion', 'fecha_actualizacion']
    
    def estado_completado(self, obj):
        """Mostrar estado de completado con color."""
        if obj.completada:
            return format_html('<span style="color: green;">✓ Completada</span>')
        else:
            # Verificar si está atrasada
            if obj.fecha_fin_estimada and obj.fecha_fin_estimada < timezone.now():
                return format_html('<span style="color: red;">⚠ Atrasada</span>')
            return format_html('<span style="color: orange;">⏳ En progreso</span>')
    estado_completado.short_description = 'Estado'
    
    actions = ['marcar_completadas', 'marcar_pendientes']
    
    def marcar_completadas(self, request, queryset):
        """Marcar tareas como completadas."""
        count = queryset.update(completada=True, fecha_fin_real=timezone.now())
        self.message_user(request, f'{count} tareas marcadas como completadas.')
    marcar_completadas.short_description = "Marcar como completadas"
    
    def marcar_pendientes(self, request, queryset):
        """Marcar tareas como pendientes."""
        count = queryset.update(completada=False, fecha_fin_real=None)
        self.message_user(request, f'{count} tareas marcadas como pendientes.')
    marcar_pendientes.short_description = "Marcar como pendientes"


@admin.register(Subtarea)
class SubtareaAdmin(BaseModelAdmin):
    """
    Configuración del admin para Subtarea.
    """
    list_display = ['nombre_subtarea', 'tarea', 'asignado_a', 'estado_completado', 'fecha_fin_estimada']
    list_filter = ['completada', 'tarea__proyecto', 'asignado_a__area']
    search_fields = ['nombre_subtarea', 'descripcion', 'tarea__nombre']
    ordering = ['tarea', 'fecha_inicio']
    
    fieldsets = (
        (None, {
            'fields': ('nombre_subtarea', 'descripcion', 'tarea', 'asignado_a')
        }),
        ('Tiempos', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real', 'duracion_estimada', 'duracion_real')
        }),
        ('Estado', {
            'fields': ('completada',)
        }),
        ('Sistema', {
            'fields': ('uuid', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['uuid', 'fecha_creacion', 'fecha_actualizacion']
    
    def estado_completado(self, obj):
        """Mostrar estado de completado con color."""
        if obj.completada:
            return format_html('<span style="color: green;">✓ Completada</span>')
        else:
            if obj.fecha_fin_estimada and obj.fecha_fin_estimada < timezone.now():
                return format_html('<span style="color: red;">⚠ Atrasada</span>')
            return format_html('<span style="color: orange;">⏳ En progreso</span>')
    estado_completado.short_description = 'Estado'


@admin.register(EmpleadosProyecto)
class EmpleadosProyectoAdmin(BaseModelAdmin):
    """
    Configuración del admin para EmpleadosProyecto.
    """
    list_display = ['empleado', 'proyecto', 'rol_en_proyecto', 'activo', 'fecha_asignacion']
    list_filter = ['activo', 'proyecto', 'empleado__area', 'fecha_asignacion']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'proyecto__nombre', 'rol_en_proyecto']
    ordering = ['-fecha_asignacion']
    date_hierarchy = 'fecha_asignacion'
    
    fieldsets = (
        (None, {
            'fields': ('empleado', 'proyecto', 'rol_en_proyecto', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_desasignacion')
        }),
        ('Sistema', {
            'fields': ('id_emple_vs_proye', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['id_emple_vs_proye', 'fecha_creacion', 'fecha_actualizacion']


# Personalización adicional del admin
admin.site.empty_value_display = '(Ninguno)'
