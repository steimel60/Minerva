from flask import Blueprint, stream_with_context, request

import aux
import db.sales
import db.organization

bp = Blueprint("sales", __name__, url_prefix="/sales")

@stream_with_context
@bp.route("/customer/purchases", methods=[ "GET", "POST" ])
def customer_purchases():
    # in future, get org from session, require session
    if request.method == "POST":
        customer = request.form.get("customer")
        if not customer:
            return "Bad Request, missing customer name", 400

        return map(
            aux.csv_transform, 
            db.sales.get_customer_purchases(
                db.organization.connect("Primal"),
                customer
            )
        ), {"Content-Type": 'text/csv'}

    return "Bad request", 404