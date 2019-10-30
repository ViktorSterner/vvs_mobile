# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import http
from odoo.http import request, Response
import werkzeug
import datetime
import base64

import logging
logger = logging.getLogger(__name__)


class ServiceMobile(http.Controller):

    @http.route('/service/all/order/', auth='user', website=True)
    def index_order(self, **kw):
        return http.request.render('service_mobile.index', {
            'root': '/service/all/order/',
            'order_ids': http.request.env['sale.order'].search([('invoice_status','!=','invoiced')]),          
        })
        
    @http.route('/service/<model("sale.order"):order>/order/', auth='user',website=True, methods=['GET','POST'])
    def update_order(self, order,**post):
        if post:
            logger.exception('kw %s' % post)
            order.note = post.get('note')
            order.prio = post.get('prio')
            for task in order.order_line:
                task.product_uom_qty = post.get('task_qty_%s' %task.id)
                if post.get('task_deliver_%s' %task.id):
                    task.qty_delivered = task.product_uom_qty
                else:
                    task.qty_delivered = 0
            logger.exception('kw %s' % order.note)
            if post.get('ufile'):
                
                # type(ufile) kan användas för att se typen på ufile
                # werkzeug.datastructures.FileStorage
                # https://werkzeug.palletsprojects.com/en/0.15.x/datastructures/
                
                # lista med mimetypes
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
                
                # hämta resultatet från formuläret
                ufile = post.get('ufile')
                
                # läs ut bildfilen.
                file_datas_bytes = ufile.read() 
                
                # file_datas_bytes är i "bytes"-format: 
                #    \xff\xd8\xff\xe1 \xfcExif\x00\x00II*\x00\x08\x00\x00\x00\x12\x00\x00\ ...
                
                # konvertera formatet till "binary" 
                # base64 är ett bibliotek med funktioner som hjälper oss med detta
                file_datas_binary = base64.b64encode(file_datas_bytes)
                                
                # file_datas_binary kommer se ut ungefär:
                #    /9j/4SD8RXhpZgAASUkqAAgAAAASAAABAwABAAAAwBwAAAEBAwABAAAAMBMAAAIBAwADA ...

                
                # logga lite...
                logger.warn("Bytes data: %s" % file_datas_bytes[:100])  # skriv ut första 100 tecknen
                logger.warn("Binary data: %s" % file_datas_binary[:100])
                
                
                
                # spara datum och klockslag NU
                current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # skapa upp en dict med våra parametrar
                attachment_params = {
                    'name': '%s %s' % (ufile.name, current_datetime),   # beskrivande namn på filen. ufile.name är fältnamnet från formuläret
                    'type': 'binary',                                   # odoo vill ha datan i binärt format
                    'datas': file_datas_binary,                         # datan som utgör filen
                    'datas_fname': ufile.filename,                      # "tekniskt" filnamn
                    'res_model': 'sale.order',                     # modell att koppla attachment till
                    'res_id': order.id,                               # id på objekt att koppla attachment till
                    'mimetype': ufile.mimetype,                         # Matcha filens mimetype
                }
                
                # skapa vår attachment med hjälp av dicten
                attachment_new = http.request.env['ir.attachment'].create(attachment_params)            

            return self.index_order()
        else:
            return http.request.render('service_mobile.view_order', {
                              'root': '/service/%s/order/' % order.id,
                              'partner_ids': http.request.env['res.partner'].search([('customer','=',True)]),
                              'attach_ids': http.request.env['ir.attachment'].search([('res_model', '=', 'sale.order'),('res_id','=', order.id)]),
                              'order': order,
                              'task_ids': order.order_line,
                              'help': {'name':'This is helpstring for name'},
                              'validation': {'name':'Warning'},
                              'input_attrs': {},
                          })

    @http.route('/service/order/create', auth='user', website=True, methods=['GET','POST'])
    def create_order(self,**post):
        # order.unlink()
        # self.index_order()
        #
        if post:
            new_order_params = {
                'partner_id': int(post.get('partner_list')),
                'template_id': int(post.get('template_list')),                
                }
            new_order = http.request.env['sale.order'].create(new_order_params)

            new_order.set_template(int(post.get('template_list')))

        else:
            return http.request.render('service_mobile.create_order',{
                'root': '/service/order/create',
                'partner_ids': http.request.env['res.partner'].search([('customer','=',True)]),
                'template_ids': http.request.env['sale.order.template'].search([]),
            })

    @http.route('/service/<model("sale.order"):order>/order/delete', auth='user')
    def delete_order(self, order,**kw):
        order.unlink()
        self.index_order()

    @http.route('/service/<model("sale.order"):order>/order/send', auth='user', website=True)
    def confirm_order(self, order,**kw):
        if order.state == "cancel":
            return self.index_order()

        else:
            template = http.request.env.ref('sale.email_template_edi_sale')
            template.write({'email_to': order.partner_id.email})
            template.send_mail(order.id, force_send=True)
            order.state = "sent"
            return self.index_order()

    @http.route('/service/<model("sale.order"):order>/order/task', auth='user',website=True, methods=['GET','POST'])
    def update_order_time(self, order,**post):
        if post:
            new_time_params = {
                'date': post.get('date_input'),
                'unit_amount': float(post.get('time_input')),
                'task_id': int(post.get('task_id')),
                'employee_id': int(post.get('user_id')),
                'account_id': int(post.get('account_id')),
                'name': post.get('desc_id'),
                }
            new_time = http.request.env['account.analytic.line'].create(new_time_params)
            return self.index_order()
            
        else:
            return http.request.render('service_mobile.view_task', {
                              'root': '/service/%s/task/' % order.id,
                              'order': order,
                              'tasks': order.tasks_ids,
                              'empolyees': http.request.env['hr.employee'].search([]),
                          })

    @http.route('/service/<model("sale.order"):order>/order/flag', type='json', auth="user", website=True)
    def post_flag(self, order, **kwargs):

        if not http.request.session.uid:
            return {'error': 'anonymous_user'}

        try:
            # Invert order.prio False -> True, True -> False
            order.prio = not order.prio
        except:
            return {'error': 'post_non_flaggable'}
        
        return {'success': 'Yes!',
                'flag_value': order.prio,
                'order_id': order.id,
            }

    @http.route('/service/<model("sale.order"):order>/order/invoice', auth="user")
    def send_invoice(self, order):
        # if order.state == "to invoice":
            invoice_id = order.action_invoice_create()
            invoice = http.request.env['account.invoice'].search([('id','=',invoice_id)])
            invoice.action_invoice_open()
            template = http.request.env.ref('account.email_template_edi_invoice')
            template.write({'email_to': invoice.partner_id.email})
            template.send_mail(invoice.id, force_send=True)
            order.state = "invoiced"

    # @http.route('/service/<model("sale.order"):order>/image', auth='user', website=True, methods=['GET','POST'])
    # def view_image(self, order, **post):
    #     attach_ids = http.request.env['ir.attachment'].search([('res_model', '=', 'sale.order'),('res_id','=', order.id)])
    #     url = attach_ids[0].website_url
    #     return url
#--------------------------------------------

    @http.route('/service/all/project/', website=True, auth='user')
    def index_project(self, **kw):
        return http.request.render('service_mobile.index_project', {
            'root': '/service/all/project/',
            'project_ids': http.request.env['project.project'].search([]),
        })
        
    @http.route('/service/<model("project.project"):project>/project/', auth='user')
    def update_project(self, project,**kw):
        
        # if post xxx
        
        return http.request.render('service_mobile.view_project', {
            'root': '/service/%s/project/' % project.id,
            'product_ids': http.request.env['product.product'].search([('is_sale','=',True)]),
            'order': order,
        })

    @http.route('/service/<model("project.project"):project>/project/delete', auth='user')
    def delete_project(self, project,**kw):
        project.unlink()
        self.index_project()

    @http.route('/service/<model("project.project"):project>/project/invoice', auth='user')
    def invoice_propject(self, order,**kw):
        project.invoice() # ?????????????
        self.index_project()

    @http.route('/partner/<int:partner_id>', website=True)
    def vcard_partner_view(self, partner_id):
        
        return http.request.render('service_mobile.partner_vcard_view', {
            'root': '/partner/%s' % partner_id,
            'partner': http.request.env['res.partner'].search([('id','=',partner_id)]),
        })
    
    @http.route('/partner/<int:partner_id>/send')
    def vcard_partner(self, partner_id):

        # Kommentarer:
        # ````````````
        # Tre stycken """ definerar en sträng som kan sträcka sig över flera rader i python.
        #
        # Funktionen format() som används nedan kommer söka på det innan likamedtecknet i 
        # strängen innan och byta ut t.ex. {name} mot det som kommer efter likamedtecknet. 
        # Nya variabler kan defineras fritt med kommatecken.
        #
        # Lättast är att ni kopierar in denna kod i ert befintliga projekt för kim och 
        # jobbar därifrån.

        partner = http.request.env['res.partner'].search([('id','=',partner_id)])


        result = """BEGIN:VCARD
            VERSION:3.0
            FN;CHARSET=UTF-8:{name}
            EMAIL;CHARSET=UTF-8;type=WORK,INTERNET:{email}
            TEL;TYPE=WORK,VOICE:{phone}
            TITLE;CHARSET=UTF-8:{title}
            ORG;CHARSET=UTF-8:{org}
            END:VCARD""".format(name=partner.name, email=partner.email,
            phone=partner.phone,title=partner.title.name,org=partner.company_name)

        return Response(result, mimetype='text/vcard')


