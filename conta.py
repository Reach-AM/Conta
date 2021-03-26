# -*- coding: utf-8 -*-
"""
@author: Ricardo Alonso
"""

# ============================================================================  
# ============================= Contabilidad =================================
# ============================================================================    

class Contabilidad:
   def __init__(self,empresa):
        self.empresa = empresa
        self.listaPartes=[0]*6  # nota: no se usa el espacio [0]
        self.listaPartes[1] = ParteContable(1,"Activo","D")
        self.listaPartes[2] = ParteContable(2,"Pasivo","A")
        self.listaPartes[3] = ParteContable(3,"Capital","A")
        self.listaPartes[4] = ParteContable(4,"Ingresos","A")
        self.listaPartes[5] = ParteContable(5,"Egresos","D")
        self.altaCta(200099,"Resultado","A")
        self.cerrado = False

   def altaCta(self,numCta,nombreCta,natCta):
       numParte = numCta // 100000
       if 1 <= numParte <= 5:
          self.listaPartes[numParte].altaCta(numCta,nombreCta,natCta)
       else:
          raise Exception("Contabilidad: el número de cuenta no es válido")
          
   def registraPoliza(self,poliza):
       # verificamos que suma de cargos sea igual a suma de abonos
       sc = 0
       sa = 0
       for m in poliza.colMovtos:
           if m.tipo == "A":
               sa += m.monto
           elif m.tipo == "C":
               sc += m.monto
           else:
               raise Exception("Tipo de movimiento inválido " + str(m))
       if sa != sc :
           raise Exception("Póliza " + str(poliza) + " ==== DESBALANCEADA ===" )
           
       # verificamos que todas las cuentas de los movimientos de la poliza existan
       for m in poliza.colMovtos:
           numParte = m.numCta // 100000
           if 1 <= numParte <= 5:
               # la parte contable arroja una excepción si la cta no existe
               self.listaPartes[numParte].verificaExistencia(m.numCta)
           else:
               raise Exception("La cta del movimiento " + str(m) + " es inválida" )
       # registramos los movimientos
       for m in poliza.colMovtos:
           numParte = m.numCta // 100000
           self.listaPartes[numParte].registraMovto(m)
       self.cerrado = False
           
   def impBalance(self):
       #Activo = Pasivo + Kapital + Ingreso - Egreso
       #CIERRE en Ingreso y Egreso (Poliza de Cierre) -> Resultado del Ejercicio
       strRes = "Balance de " + self.empresa + '\n'
       strBal = ""
       cuenta = 0.0
       for p in self.listaPartes[1:]:
            strRes += p.impBalance()
            strBal += str(p.saldo().monto)
            if p.num == 1:
                strBal += " = "
            elif p.num < 4:
                cuenta += p.saldo().monto
                strBal += " + "  
            elif p.num < 5:
                cuenta += p.saldo().monto
                strBal += " - "
            else:
                cuenta -= p.saldo().monto
       strRes += 61 * '_' + '\n' 
       strRes += "\nActivo = Pasivo + Kapital + Ingreso - Egreso\n"
       strRes += strBal + "\n"
       strRes += str(self.listaPartes[1].saldo().monto) + " = " + str(cuenta) + "\n"
       return strRes
   
   def cierre(self):
       for i in range(2):
           for c in self.listaPartes[i+4].colCtas.values():
               saldoCta = c.saldo().monto
               if saldoCta != 0:
                   pol_cierre = PolizaContable(0,"2019-12-31","Ajuste de Cuenta")
                   if self.listaPartes[i+4].nat == "A":
                       pol_cierre.abono(200099,saldoCta)
                       pol_cierre.cargo(c.num,saldoCta)
                   else:
                       pol_cierre.abono(c.num,saldoCta)
                       pol_cierre.cargo(200099,saldoCta)
                       
                   self.registraPoliza(pol_cierre)
       self.cerrado = True
                   
               
   
   def __str__(self):
       strRes = "Contabilidad " + self.empresa + '\n'
       if not self.cerrado:
           strRes += "(Res. del Ejercicio sin ajustar)\n"
       for x in self.listaPartes[1:]:
           strRes += str(x)
       return strRes    
   
# ============================================================================  
# ============================ ParteContable =================================
# ============================================================================    
   
class ParteContable:
    def __init__(self, numParte, nombreParte,natParte):
        self.num    = numParte
        self.nombre = nombreParte
        self.nat    = natParte
        self.colCtas = {} #Colección indexada 
     
    def altaCta(self,numCta,nombreCta, natCta):
        if self.colCtas.get(numCta) == None:
            self.colCtas[numCta] = CtaT(numCta,nombreCta,natCta)
        else:
            raise Exception("La cuenta " + str(numCta) + " " + nombreCta + " (" + natCta + ") ya existe")
            
    def verificaExistencia(self,numCta):
        if self.colCtas.get(numCta) == None:
            raise Exception("La cta " + str(numCta) + " no existe")
    
    def registraMovto(self,m):
         cta = self.colCtas.get(m.numCta)
         cta.registraMovto(m)

    def saldo(self):
        sdoCtasD = 0
        sdoCtasA = 0
        for cta in self.colCtas.values():
            if cta.nat == "D":
                sdoCtasD += cta.saldo().monto
            else:
                sdoCtasA += cta.saldo().monto
        if self.nat == "D":
            m_sdo = MovtoConta(0,1,sdoCtasD - sdoCtasA,"C")
        else:
            m_sdo = MovtoConta(0,1,sdoCtasA - sdoCtasD,"A")
        return m_sdo
           
    def impSaldo(self):
        sdo = self.saldo()
        strRes = iif(sdo.tipo=='A',35,20) * ' ' + '{:12.2f}'.format(sdo.monto) + '\n'
        return strRes

    def impBalance(self): 
       strRes = '_' * 61 + '\n' + \
                '{:25}'.format(str(self.num) + '(' + self.nat + ') ' + self.nombre + 5*' ') + '\n'
       for cta in self.colCtas.values():
           strRes += cta.impBalance()
       strRes += '=' * 51  +'\n'  
       strRes += self.impSaldo()
       return strRes    
                
    def __str__(self):
       strRes = '_' * 51 + '\n' + \
                '{:40}'.format("Parte Contable " + str(self.num) + " " + self.nombre + 20*' ') + \
                " (" + self.nat + ")\n"          
       for cta in self.colCtas.values():
           strRes += str(cta)
       strRes += self.impSaldo()    
       return strRes    

# ============================================================================  
# ================================ CtaT ======================================
# ============================================================================    

class CtaT:
    def __init__(self,numCta,nombreCta,natCta):
        self.num = numCta
        self.nombre = nombreCta
        self.nat = natCta
        self.colMovtos = []
        
    def registraMovto(self,m):
        self.colMovtos.append(m)
    
    def saldo(self):
        sc = 0
        sa = 0
        for m in self.colMovtos:
            if m.tipo == "C":
                sc += m.monto
            else:
                sa += m.monto
        if self.nat == "D":
            m_sdo = MovtoConta(0,1,sc - sa,"C")
        else:
            m_sdo = MovtoConta(0,1,sa - sc,"A")
        return m_sdo   
    
    def impBalance(self):
        sdo = self.saldo()
        strRes = "  " + \
                '{:25}'.format(str(self.num) + ' ' + self.nombre) + ' (' + self.nat + ')' 
        strRes += iif(sdo.tipo=='A',15,0) * ' ' + '{:12.2f}'.format(sdo.monto) + '\n'
        return strRes

    def impSaldo(self):
        sdo = self.saldo()
        strRes = iif(sdo.tipo=='A',35,20) * ' ' + '{:12.2f}'.format(sdo.monto)
        return strRes

    
    def __str__(self):
        strRes = "  " + \
                '{:40}'.format(str(self.num) + ' ' + self.nombre) + ' (' + self.nat + ')' + '\n' + \
                51 * '-' + '\n'
        for m in self.colMovtos:
            strRes += str(m)
        if len(self.colMovtos) > 0:
          strRes += 51 * '-' + '\n'    
        strRes += self.impSaldo() + '\n'
        strRes += 51 * '-' + '\n'  
        return strRes

# ============================================================================  
# ============================= PolizaContable ===============================
# ============================================================================    

class PolizaContable:
    def __init__(self,numPoliza,fecha,descripcion):
        self.numPoliza   = numPoliza
        self.fecha       = fecha
        self.descripcion = descripcion
        self.colMovtos = []
        
    def cargo(self,numCta,monto):
        self.colMovtos.append(MovtoConta(self.numPoliza,numCta,monto,'C'))
    def abono(self,numCta,monto):
        self.colMovtos.append(MovtoConta(self.numPoliza,numCta,monto,'A'))
        
    def __str__(self):
        strRes = "Póliza num " + str(self.numPoliza) + " " + self.fecha + " " + self.descripcion + '\n'
        for m in self.colMovtos:
            strRes += str(m) 
        return strRes    

# ============================================================================  
# ============================== MovtoConta ==================================
# ============================================================================    
            
class MovtoConta:
    def __init__(self,numPoliza,numCta,monto,c_a):
        self.numPoliza = numPoliza
        self.numCta    = numCta
        self.monto     = monto
        self.tipo      = c_a
        
    def __str__(self):
        strRes = "  " + '{:5d}'.format(self.numPoliza) + ')' + 5*' ' + str(self.numCta)
        strRes += iif(self.tipo == "A", 20,5) * ' '
        strRes += '{:12.2f}'.format(self.monto) + '\n'
        return strRes

# ============================================================================  
# ================================== iif =====================================
# ============================================================================  

def iif(cond,vt,vf):
    if cond:
        res = vt
    else:
        res = vf
    return res  
           
# =======================================================================================
#                                         script de prueba         
# =======================================================================================
conta = Contabilidad("MiEmpre S.A.")
conta.altaCta(100100,"Bancos","D")
conta.altaCta(100200,"Inventario","D")
conta.altaCta(100300,"Clientes","D")
conta.altaCta(200100,"Proveedores","A")
conta.altaCta(300000,"Capital","A")
conta.altaCta(400100,"Ventas","A")
conta.altaCta(500100,"Costo de lo vendido","D")
# print('\nPosterior al alta de las cuentas')
# print(conta)        
# print("===============================================")
pol_1 = PolizaContable(1,"2019-010-04", "Creación de la empresa")
pol_1.cargo(100100,100000.0)
pol_1.abono(300000,100000.0)
#print(pol_1)
# print("===============================================")
conta.registraPoliza(pol_1)
# print('\nPosterior al registro de la póliza 1')
# print("===============================================")
pol_2 = PolizaContable(2,"2019-10-05","Compra de mercancía para vender")
pol_2.abono(100100,20000.0) # Se paga al contado
pol_2.cargo(100200,20000.0) # Se guarda en el almacen (Inventario)
# print("===============================================")
conta.registraPoliza(pol_2)
# print('\nPosterior al registro de la póliza 2')
# print(conta)
# print("++++++++++++++++++++++++++++++++++++++++++++++++")
pol_3 = PolizaContable(3,"2019-10-06","Venta en 1500.0, al contado de mercancia que costó 1000.0")
pol_3.abono(100200,1000.0)
pol_3.cargo(500100,1000.0)
pol_3.abono(400100,1500.0)
pol_3.cargo(100100,1500.0)
# print("===============================================")
conta.registraPoliza(pol_3)
# print('\nPosterior al registro de la póliza 3')
# print(conta)
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
pol_4 = PolizaContable(4,"2019-10-07","Venta en 1000.0, al contado de mercancia que costó 750.0")
pol_4.abono(100200,750.0)
pol_4.cargo(500100,750.0)
pol_4.abono(400100,1000.0)
pol_4.cargo(100100,1000.0)
# print("===============================================")
conta.registraPoliza(pol_4)
#print('\nPosterior al registro de la póliza 4')
# print(conta)
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
pol_5 = PolizaContable(5,"2019-10-07","Venta en 5000.0, al contado de mercancia que costó 3750.0")
pol_5.abono(100200,3750.0)
pol_5.cargo(500100,3750.0)
pol_5.abono(400100,5000.0)
pol_5.cargo(100100,5000.0)
# print("===============================================")
conta.registraPoliza(pol_5)
#print('\nPosterior al registro de la póliza 5')
print("===============================================")
print("Antes del 1º Resultado del Ejercicio")
print("===============================================")
print("\n" + str(conta))
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
print(conta.impBalance())
conta.cierre() #Se realiza el cierre (registrado con 0 en la cuenta 200099)
print("===============================================")
print('Después del 1º Resultado del Ejercicio')
print("===============================================")
print("\n" + str(conta))
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
print(conta.impBalance())
pol_6 = PolizaContable(6,"2019-10-07","Venta en 2000.0, al contado de mercancia que costó 1500.0")
pol_6.abono(100200,1500.0)
pol_6.cargo(500100,1500.0)
pol_6.abono(400100,2000.0)
pol_6.cargo(100100,2000.0)
conta.registraPoliza(pol_6)
print("===============================================")
print('Posterior al registro de la póliza 6')
print("===============================================")
print("\n" + str(conta))
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
print(conta.impBalance())
conta.cierre()
print("===============================================")
print('Después del 2º Resultado del Ejercicio')
print("===============================================")
print("\n" + str(conta))
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
print(conta.impBalance())
