/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package dao.custom.impl;

import dao.CrudUtill;
import dao.custom.HostelDAO;
import entity.Hostel;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

/**
 *
 * @author Ashen Koralage
 */
public class HostelDAOImpl implements HostelDAO {

    @Override
    public boolean add(Hostel hostel) throws ClassNotFoundException, SQLException {
        return CrudUtill.executeUpdate("insert into hostel values(?,?,?,?,?)", hostel.getHID(), hostel.getNo_of_Rooms(), hostel.getGender_of_residence(), hostel.getPhone_Number(), hostel.getAddress());

    }

    @Override
    public boolean update(Hostel t) throws ClassNotFoundException, SQLException {
        return CrudUtill.executeUpdate("update hostel set No_of_Rooms=?, Gender_of_residence=?,phone_Number=?,Address=? where HID=?", t.getNo_of_Rooms(), t.getGender_of_residence(), t.getPhone_Number(), t.getAddress(), t.getHID());
    }

    @Override
    public boolean delete(String t) throws ClassNotFoundException, SQLException {
        return CrudUtill.executeUpdate("delete from hostel where HID=?", t);
    }

    @Override
    public Hostel search(String t) throws ClassNotFoundException, SQLException {

        ResultSet rst = CrudUtill.executeQuery("select * from hostel where HID=?", t);
        Hostel hostel = null;
        if (rst.next()) {
            hostel = new Hostel(rst.getString(1), rst.getString(2), rst.getString(3), rst.getString(4), rst.getString(5));
        }
        return hostel;
    }

    @Override
    public ArrayList<Hostel> getAll() throws ClassNotFoundException, SQLException {
        ResultSet rst = CrudUtill.executeQuery("select * from hostel");
        ArrayList<Hostel> allHostels = new ArrayList<>();
        while (rst.next()) {
            allHostels.add(new Hostel(rst.getString(1), rst.getString(2), rst.getString(3), rst.getString(4), rst.getString(5)));
        }
        return allHostels;

    }

    @Override
    public ArrayList<Hostel> getAllAvailableHostels() throws ClassNotFoundException, SQLException {
        ResultSet rst = CrudUtill.executeQuery("select distinct h.* from hostel h "
                + "join room r on h.HID = r.HID "
                + "where r.Current_Borders_count < r.No_of_beds");
        ArrayList<Hostel> allAvailableHostels = new ArrayList<>();
        while (rst.next()) {
            allAvailableHostels.add(new Hostel(rst.getString(1), rst.getString(2), rst.getString(3), rst.getString(4), rst.getString(5)));
        }
        return allAvailableHostels;
    }

}
