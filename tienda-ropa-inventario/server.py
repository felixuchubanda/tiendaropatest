from concurrent import futures
import grpc
import inventario_pb2
import inventario_pb2_grpc

productos = []

class InventarioServicer(inventario_pb2_grpc.InventarioServicer):
    def CrearProducto(self, request, context):
        productos.append(request)
        return inventario_pb2.Respuesta(mensaje='Producto creado')

    def ObtenerProducto(self, request, context):
        producto = next((p for p in productos if p.id == request.id), None)
        if producto:
            return producto
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Producto no encontrado')
        return inventario_pb2.Producto()

    def ActualizarProducto(self, request, context):
        global productos
        index = next((i for i, p in enumerate(productos) if p.id == request.id), None)
        if index is not None:
            productos[index] = request
            return inventario_pb2.Respuesta(mensaje='Producto actualizado')
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Producto no encontrado')
        return inventario_pb2.Respuesta(mensaje='Producto no encontrado')

    def EliminarProducto(self, request, context):
        global productos
        productos = [p for p in productos if p.id != request.id]
        return inventario_pb2.Respuesta(mensaje='Producto eliminado')

    def ListarProductos(self, request, context):
        return inventario_pb2.ListaProductos(productos=productos)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventario_pb2_grpc.add_InventarioServicer_to_server(InventarioServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Servidor gRPC ejecutándose en [::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
